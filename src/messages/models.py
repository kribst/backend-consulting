from django.db import models


class ContactMessage(models.Model):
	class Status(models.TextChoices):
		NOUVEAU = "nouveau", "Nouveau"
		EN_COURS = "en_cours", "En cours"
		TRAITE = "traite", "Traite"
		ARCHIVE = "archive", "Archive"

	nom = models.CharField(max_length=150)
	email = models.EmailField()
	telephone = models.CharField(max_length=30, blank=True)
	entreprise = models.CharField(max_length=150, blank=True)
	service_id = models.PositiveIntegerField(null=True, blank=True)
	service = models.CharField(max_length=200, blank=True)
	sujet = models.CharField(max_length=255)
	message = models.TextField()
	statut = models.CharField(max_length=20, choices=Status.choices, default=Status.NOUVEAU)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.nom} - {self.sujet}"
