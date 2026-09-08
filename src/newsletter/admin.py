from django.conf import settings
from django.contrib import admin, messages
from django.core.mail import get_connection, send_mail
from django import forms

from .models import NewsletterCampaign, NewsletterSubscriber, SMTPConfiguration


@admin.register(SMTPConfiguration)
class SMTPConfigurationAdmin(admin.ModelAdmin):
	list_display = ("host", "port", "username", "from_email", "use_ssl", "use_tls", "updated_at")
	readonly_fields = ("updated_at",)
	fieldsets = (
		("Connexion", {"fields": ("host", "port", "username", "password", "timeout")}),
		("Sécurité", {"fields": ("use_ssl", "use_tls")}),
		("Expéditeur", {"fields": ("from_email",)}),
		("Mise à jour", {"fields": ("updated_at",)}),
	)
	actions = ("envoyer_email_test",)

	def formfield_for_dbfield(self, db_field, request, **kwargs):
		field = super().formfield_for_dbfield(db_field, request, **kwargs)
		if db_field.name == "password":
			field.widget = forms.PasswordInput(render_value=True)
		return field

	def has_add_permission(self, request):
		return not SMTPConfiguration.objects.exists()

	def get_changeform_initial_data(self, request):
		return {
			"host": settings.EMAIL_HOST,
			"port": settings.EMAIL_PORT,
			"username": settings.EMAIL_HOST_USER,
			"password": settings.EMAIL_HOST_PASSWORD,
			"use_ssl": settings.EMAIL_USE_SSL,
			"use_tls": settings.EMAIL_USE_TLS,
			"from_email": settings.DEFAULT_FROM_EMAIL,
			"timeout": settings.EMAIL_TIMEOUT,
		}

	@admin.action(description="Envoyer un email de test à mon adresse")
	def envoyer_email_test(self, request, queryset):
		configuration = queryset.first()
		if configuration is None:
			self.message_user(request, "Sélectionnez une configuration SMTP.", messages.ERROR)
			return
		try:
			connection = get_connection(
				backend="django.core.mail.backends.smtp.EmailBackend",
				host=configuration.host,
				port=configuration.port,
				username=configuration.username,
				password=configuration.password,
				use_ssl=configuration.use_ssl,
				use_tls=configuration.use_tls,
				timeout=configuration.timeout,
			)
			send_mail(
				"Test de configuration SMTP",
				"La configuration SMTP de FALKAOH CONSULTING fonctionne correctement.",
				configuration.from_email,
				[request.user.email],
				connection=connection,
				fail_silently=False,
			)
			self.message_user(request, f"Email de test envoyé à {request.user.email}.", messages.SUCCESS)
		except Exception as exc:
			self.message_user(request, f"Échec de l'envoi : {exc}", messages.ERROR)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
	list_display = ("email", "nom", "statut", "source", "subscribed_at", "unsubscribed_at")
	list_filter = ("statut", "source", "subscribed_at")
	search_fields = ("email", "nom")
	readonly_fields = ("subscribed_at", "unsubscribed_at", "ip_address", "user_agent")
	ordering = ("-subscribed_at",)
	date_hierarchy = "subscribed_at"

	fieldsets = (
		(None, {"fields": ("email", "nom", "statut", "source")}),
		(
			"Métadonnées",
			{"fields": ("ip_address", "user_agent", "subscribed_at", "unsubscribed_at")},
		),
	)

	actions = ["marquer_comme_actif", "marquer_comme_desabonne"]

	@admin.action(description="Marquer comme actif")
	def marquer_comme_actif(self, request, queryset):
		queryset.update(statut=NewsletterSubscriber.Status.ACTIF, unsubscribed_at=None)

	@admin.action(description="Marquer comme désabonné")
	def marquer_comme_desabonne(self, request, queryset):
		from django.utils import timezone

		queryset.update(statut=NewsletterSubscriber.Status.DESABONNE, unsubscribed_at=timezone.now())


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
	list_display = ("sujet", "audience", "statut", "destinataires_count", "envoyee_at", "envoye_par")
	list_filter = ("statut", "audience", "created_at")
	search_fields = ("sujet", "message")
	readonly_fields = ("statut", "destinataires_count", "envoyee_at", "created_at", "envoye_par")
	date_hierarchy = "created_at"
