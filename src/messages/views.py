from django.db.models import Q
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContactMessage
from .serializers import (
	ContactMessageCreateSerializer,
	ContactMessageSerializer,
	ContactMessageStatusSerializer,
	ContactMessageReplySerializer,
)
from newsletter.models import SMTPConfiguration
from content.models import SiteContent


class PublicContactMessageView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = ContactMessageCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		message = serializer.save()
		return Response({
			"message": "Votre message a été envoyé avec succès.",
			"data": {"id": message.id, "statut": message.statut},
		}, status=status.HTTP_201_CREATED)


class AdminDashboardView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		counts = {
			value: ContactMessage.objects.filter(statut=value).count()
			for value, _label in ContactMessage.Status.choices
		}
		recent_messages = ContactMessage.objects.all()[:5]
		return Response({"data": {
			**counts,
			"total": ContactMessage.objects.count(),
			"recent_messages": ContactMessageSerializer(recent_messages, many=True).data,
		}})


class AdminMessageListView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		messages = ContactMessage.objects.all()
		search = request.query_params.get("recherche", "").strip()
		statut = request.query_params.get("statut", "").strip()
		if search:
			messages = messages.filter(
				Q(nom__icontains=search)
				| Q(email__icontains=search)
				| Q(telephone__icontains=search)
				| Q(entreprise__icontains=search)
				| Q(service__icontains=search)
				| Q(sujet__icontains=search)
			)
		if statut:
			messages = messages.filter(statut=statut)
		return Response({"data": ContactMessageSerializer(messages, many=True).data})


class AdminMessageDetailView(APIView):
	permission_classes = [IsAuthenticated]

	def get_object(self, pk):
		return ContactMessage.objects.filter(pk=pk).first()

	def get(self, request, pk):
		message = self.get_object(pk)
		if message is None:
			return Response({"message": "Message introuvable."}, status=status.HTTP_404_NOT_FOUND)
		return Response({"data": ContactMessageSerializer(message).data})


class AdminMessageStatusView(APIView):
	permission_classes = [IsAuthenticated]

	def patch(self, request, pk):
		message = ContactMessage.objects.filter(pk=pk).first()
		if message is None:
			return Response({"message": "Message introuvable."}, status=status.HTTP_404_NOT_FOUND)
		serializer = ContactMessageStatusSerializer(message, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"data": ContactMessageSerializer(message).data})


class AdminMessageDeleteView(APIView):
	permission_classes = [IsAuthenticated]

	def delete(self, request, pk):
		message = ContactMessage.objects.filter(pk=pk).first()
		if message is None:
			return Response({"message": "Message introuvable."}, status=status.HTTP_404_NOT_FOUND)
		message.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

class AdminMessageReplyView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, pk):
		contact_message = ContactMessage.objects.filter(pk=pk).first()
		if contact_message is None:
			return Response({"message": "Message introuvable."}, status=status.HTTP_404_NOT_FOUND)

		serializer = ContactMessageReplySerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
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

		try:
			connection = get_connection(**mail_options)
			site_content = SiteContent.objects.first()
			company = site_content.company if site_content else {}
			text_message = serializer.validated_data["message"]
			subject = serializer.validated_data["sujet"]
			company_website = company.get("website", "")
			company_logo = f"{settings.PUBLIC_SITE_URL.rstrip('/')}{settings.STATIC_URL}logo.png"
			email_context = {
				"sujet": subject,
				"message": text_message,
				"recipient_name": contact_message.nom,
				"company": {
					"name": company.get("name", "FALKAOH CONSULTING"),
					"logo_url": company_logo,
					"logo_alt": company.get("logoAlt", "Logo FALKAOH CONSULTING"),
					"address": company.get("address", ""),
					"phone": company.get("phone", ""),
					"email": company.get("email", from_email),
					"website": company.get("website", ""),
				},
			}
			html_message = render_to_string("emails/contact_reply.html", email_context)
			email = EmailMultiAlternatives(
				subject,
				text_message,
				from_email,
				[contact_message.email],
				connection=connection,
			)
			email.attach_alternative(html_message, "text/html")
			email.send(fail_silently=False)
			return Response({"message": f"Réponse envoyée à {contact_message.email}."})
		except Exception as exc:
			return Response({"message": f"Échec de l'envoi : {exc}"}, status=status.HTTP_502_BAD_GATEWAY)
# Create your views here.
