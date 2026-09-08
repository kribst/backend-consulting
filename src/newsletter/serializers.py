from rest_framework import serializers

from .models import NewsletterCampaign, NewsletterSubscriber


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
	class Meta:
		model = NewsletterSubscriber
		fields = (
			"id",
			"email",
			"nom",
			"statut",
			"source",
			"subscribed_at",
			"unsubscribed_at",
		)
		read_only_fields = (
			"id",
			"statut",
			"source",
			"subscribed_at",
			"unsubscribed_at",
		)


class NewsletterSubscribeSerializer(serializers.Serializer):
	email = serializers.EmailField()
	nom = serializers.CharField(required=False, allow_blank=True, max_length=150)

	def create(self, validated_data):
		email = validated_data["email"]
		request = self.context.get("request")

		subscriber, created = NewsletterSubscriber.objects.get_or_create(
			email=email,
			defaults={
				"nom": validated_data.get("nom", ""),
				"source": "site",
				"ip_address": self._client_ip(request),
				"user_agent": self._user_agent(request),
				"statut": NewsletterSubscriber.Status.ACTIF,
			},
		)

		if not created and subscriber.statut == NewsletterSubscriber.Status.DESABONNE:
			subscriber.statut = NewsletterSubscriber.Status.ACTIF
			subscriber.unsubscribed_at = None
			subscriber.save(update_fields=["statut", "unsubscribed_at"])

		return subscriber, created

	def _client_ip(self, request):
		if not request:
			return None
		for header in ("HTTP_X_FORWARDED_FOR", "HTTP_X_REAL_IP"):
			value = request.META.get(header)
			if value:
				return value.split(",")[0].strip()
		return request.META.get("REMOTE_ADDR")

	def _user_agent(self, request):
		if not request:
			return ""
		return request.META.get("HTTP_USER_AGENT", "")[:255]


class NewsletterCampaignSerializer(serializers.ModelSerializer):
	class Meta:
		model = NewsletterCampaign
		fields = (
			"id",
			"sujet",
			"message",
			"audience",
			"statut",
			"destinataires_count",
			"envoyee_at",
			"created_at",
		)
		read_only_fields = ("id", "statut", "destinataires_count", "envoyee_at", "created_at")
