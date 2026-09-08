from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NewsletterCampaign, NewsletterSubscriber, SMTPConfiguration
from content.models import SiteContent
from .serializers import (
	NewsletterCampaignSerializer,
	NewsletterSubscribeSerializer,
	NewsletterSubscriberSerializer,
)


class PublicNewsletterSubscribeView(APIView):
	authentication_classes = []
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = NewsletterSubscribeSerializer(data=request.data, context={"request": request})
		serializer.is_valid(raise_exception=True)
		subscriber, created = serializer.save()

		message = (
			"Votre abonnement a bien été enregistré."
			if created
			else "Cet email est déjà inscrit à la newsletter."
		)
		return Response(
			{
				"message": message,
				"data": {
					"id": subscriber.id,
					"email": subscriber.email,
					"nouveau": created,
				},
			},
			status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
		)


class AdminNewsletterListView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		subscribers = NewsletterSubscriber.objects.all()
		recherche = request.query_params.get("recherche", "").strip()
		statut = request.query_params.get("statut", "").strip()

		if recherche:
			from django.db.models import Q

			subscribers = subscribers.filter(
				Q(email__icontains=recherche) | Q(nom__icontains=recherche)
			)

		if statut:
			subscribers = subscribers.filter(statut=statut)

		total = NewsletterSubscriber.objects.count()
		actifs = NewsletterSubscriber.objects.filter(statut=NewsletterSubscriber.Status.ACTIF).count()
		desabonnes = NewsletterSubscriber.objects.filter(
			statut=NewsletterSubscriber.Status.DESABONNE
		).count()

		return Response(
			{
				"data": {
					"total": total,
					"actifs": actifs,
					"desabonnes": desabonnes,
					"subscribers": NewsletterSubscriberSerializer(subscribers, many=True).data,
				}
			}
		)


class AdminNewsletterStatusView(APIView):
	permission_classes = [IsAuthenticated]

	def patch(self, request, pk):
		subscriber = NewsletterSubscriber.objects.filter(pk=pk).first()
		if subscriber is None:
			return Response(
				{"message": "Abonné introuvable."},
				status=status.HTTP_404_NOT_FOUND,
			)

		new_status = request.data.get("statut")
		if new_status not in dict(NewsletterSubscriber.Status.choices):
			return Response(
				{"message": "Statut invalide."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		subscriber.statut = new_status
		if new_status == NewsletterSubscriber.Status.DESABONNE:
			subscriber.unsubscribed_at = timezone.now()
		else:
			subscriber.unsubscribed_at = None
		subscriber.save(update_fields=["statut", "unsubscribed_at"])

		return Response({"data": NewsletterSubscriberSerializer(subscriber).data})


class AdminNewsletterDeleteView(APIView):
	permission_classes = [IsAuthenticated]

	def delete(self, request, pk):
		subscriber = NewsletterSubscriber.objects.filter(pk=pk).first()
		if subscriber is None:
			return Response(
				{"message": "Abonné introuvable."},
				status=status.HTTP_404_NOT_FOUND,
			)
		subscriber.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class AdminNewsletterCampaignView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		campaigns = NewsletterCampaign.objects.all()[:50]
		return Response({"data": NewsletterCampaignSerializer(campaigns, many=True).data})

	def post(self, request):
		sujet = (request.data.get("sujet") or "").strip()
		message = (request.data.get("message") or "").strip()
		audience = request.data.get("audience") or NewsletterCampaign.Audience.ACTIFS
		subscriber_ids = request.data.get("subscriber_ids") or []

		if not sujet or not message:
			return Response(
				{"message": "Le sujet et le message sont obligatoires."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if audience not in dict(NewsletterCampaign.Audience.choices):
			return Response(
				{"message": "Audience invalide."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		queryset = NewsletterSubscriber.objects.all()
		if audience == NewsletterCampaign.Audience.ACTIFS:
			queryset = queryset.filter(statut=NewsletterSubscriber.Status.ACTIF)
		elif audience == NewsletterCampaign.Audience.DESABONNES:
			queryset = queryset.filter(statut=NewsletterSubscriber.Status.DESABONNE)
		elif audience == NewsletterCampaign.Audience.SELECTION:
			if not isinstance(subscriber_ids, list) or not subscriber_ids:
				return Response(
					{"message": "Aucun destinataire sélectionné."},
					status=status.HTTP_400_BAD_REQUEST,
				)
			queryset = queryset.filter(id__in=subscriber_ids)

		recipients = list(queryset.values_list("email", flat=True))
		if not recipients:
			return Response(
				{"message": "Aucun destinataire trouvé pour cette audience."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		configuration = SMTPConfiguration.objects.first()
		mail_options = {
			"backend": "django.core.mail.backends.smtp.EmailBackend",
			"host": configuration.host if configuration else settings.EMAIL_HOST,
			"port": configuration.port if configuration else settings.EMAIL_PORT,
			"username": configuration.username if configuration else settings.EMAIL_HOST_USER,
			"password": configuration.password if configuration else settings.EMAIL_HOST_PASSWORD,
			"use_ssl": configuration.use_ssl if configuration else settings.EMAIL_USE_SSL,
			"use_tls": configuration.use_tls if configuration else settings.EMAIL_USE_TLS,
			"timeout": configuration.timeout if configuration else settings.EMAIL_TIMEOUT,
		}
		from_email = configuration.from_email if configuration else settings.DEFAULT_FROM_EMAIL
		connection = get_connection(**mail_options)

		try:
			site_content = SiteContent.objects.first()
			company = site_content.company if site_content else {}
			company_logo = f"{settings.PUBLIC_SITE_URL.rstrip('/')}{settings.STATIC_URL}logo.png"
			company_data = {
				"name": company.get("name", "FALKAOH CONSULTING"),
				"logo_url": company_logo,
				"logo_alt": company.get("logoAlt", "Logo FALKAOH CONSULTING"),
				"address": company.get("address", ""),
				"phone": company.get("phone", ""),
				"email": company.get("email", from_email),
				"website": company.get("website", ""),
			}
			recipient_name_by_email = dict(
				queryset.values_list("email", "nom")
			)
			for recipient in recipients:
				recipient_name = recipient_name_by_email.get(recipient, "") or ""
				unsubscribe_url = f"{settings.PUBLIC_SITE_URL.rstrip('/')}/newsletter/desabonner?email={recipient}"
				html_message = render_to_string("emails/contact_reply.html", {
					"sujet": sujet,
					"message": message,
					"recipient_name": recipient_name,
					"company": company_data,
					"unsubscribe_url": unsubscribe_url,
				})
				email = EmailMultiAlternatives(
					sujet,
					message,
					from_email,
					[recipient],
					connection=connection,
				)
				email.attach_alternative(html_message, "text/html")
				email.send(fail_silently=False)
			campaign = NewsletterCampaign.objects.create(
				sujet=sujet,
				message=message,
				audience=audience,
				statut=NewsletterCampaign.Status.ENVOYEE,
				envoye_par=request.user if request.user.is_authenticated else None,
				destinataires_count=len(recipients),
				envoyee_at=timezone.now(),
			)
			return Response(
				{
					"message": f"Campagne envoyée à {len(recipients)} abonné(s).",
					"data": NewsletterCampaignSerializer(campaign).data,
				}
			)
		except Exception as exc:
			campaign = NewsletterCampaign.objects.create(
				sujet=sujet,
				message=message,
				audience=audience,
				statut=NewsletterCampaign.Status.ECHOUEE,
				envoye_par=request.user if request.user.is_authenticated else None,
				destinataires_count=len(recipients),
			)
			return Response(
				{
					"message": f"Échec de l'envoi : {exc}",
					"data": NewsletterCampaignSerializer(campaign).data,
				},
				status=status.HTTP_502_BAD_GATEWAY,
			)
