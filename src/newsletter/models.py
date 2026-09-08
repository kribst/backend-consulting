from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class SMTPConfiguration(models.Model):
	host = models.CharField(max_length=255, default="frigo.o2switch.net")
	port = models.PositiveIntegerField(default=465)
	username = models.EmailField()
	password = models.CharField(max_length=255)
	use_ssl = models.BooleanField(default=True)
	use_tls = models.BooleanField(default=False)
	from_email = models.EmailField()
	timeout = models.PositiveIntegerField(default=20)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Configuration SMTP"
		verbose_name_plural = "Configuration SMTP"

	def clean(self):
		if self.use_ssl and self.use_tls:
			raise ValidationError("SSL et TLS ne peuvent pas être activés simultanément.")
		if not self.from_email:
			self.from_email = self.username

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.username} ({self.host}:{self.port})"


class NewsletterSubscriber(models.Model):
	class Status(models.TextChoices):
		ACTIF = "actif", "Actif"
		DESABONNE = "desabonne", "Désabonné"

	email = models.EmailField(unique=True)
	nom = models.CharField(max_length=150, blank=True)
	statut = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIF)
	source = models.CharField(max_length=80, blank=True, default="site")
	ip_address = models.GenericIPAddressField(null=True, blank=True)
	user_agent = models.CharField(max_length=255, blank=True)
	subscribed_at = models.DateTimeField(auto_now_add=True)
	unsubscribed_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-subscribed_at"]

	def __str__(self):
		return self.email


class NewsletterCampaign(models.Model):
	class Audience(models.TextChoices):
		ALL = "all", "Tous les abonnés"
		ACTIFS = "actifs", "Abonnés actifs uniquement"
		DESABONNES = "desabonnes", "Désabonnés uniquement"
		SELECTION = "selection", "Sélection manuelle"

	class Status(models.TextChoices):
		DRAFT = "brouillon", "Brouillon"
		ENVOYEE = "envoyee", "Envoyée"
		ECHOUEE = "echouee", "Échouée"

	sujet = models.CharField(max_length=255)
	message = models.TextField()
	audience = models.CharField(
		max_length=20, choices=Audience.choices, default=Audience.ACTIFS
	)
	statut = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
	envoye_par = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="newsletter_campaigns",
	)
	destinataires_count = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	envoyee_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.sujet} ({self.get_statut_display()})"
