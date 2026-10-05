from django.db import models


class SiteContent(models.Model):
	company = models.JSONField(default=dict)
	services = models.JSONField(default=list)
	actualites = models.JSONField(default=list)
	statistics = models.JSONField(default=list)
	testimonials = models.JSONField(default=list)
	process_steps = models.JSONField(default=list)
	seo = models.JSONField(default=dict)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Contenu du site"
		verbose_name_plural = "Contenu du site"

	def __str__(self):
		return "Contenu principal du site"


class Actualite(models.Model):
	slug = models.SlugField(max_length=200, unique=True)
	title = models.CharField(max_length=255)
	category = models.CharField(max_length=120)
	datePublication = models.DateField()
	heurePublication = models.TimeField()
	image = models.ImageField(upload_to="images/actualites/", blank=True)
	imageAlt = models.CharField(max_length=255)
	content = models.JSONField(default=list)
	position = models.PositiveIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Actualité"
		verbose_name_plural = "Actualités"
		ordering = ["position", "id"]

	def __str__(self):
		return self.title


class Service(models.Model):
	title = models.CharField(max_length=255)
	slug = models.CharField(max_length=255, unique=True)
	icon = models.CharField(max_length=100)
	summary = models.TextField()
	description = models.TextField()
	image = models.ImageField(upload_to="images/services/", blank=True)
	imageAlt = models.CharField(max_length=255)
	keyPoints = models.JSONField(default=list)
	includes = models.JSONField(default=list)
	audience = models.JSONField(default=list)
	benefits = models.JSONField(default=list)
	useCases = models.JSONField(default=list)
	process = models.JSONField(default=list)
	relatedSlugs = models.JSONField(default=list)
	position = models.PositiveIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Service"
		verbose_name_plural = "Services"
		ordering = ["position", "id"]

	def __str__(self):
		return self.title


class Testimonial(models.Model):
	name = models.CharField(max_length=150)
	role = models.CharField(max_length=150)
	quote = models.CharField(max_length=500)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Témoignage"
		verbose_name_plural = "Témoignages"
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.name} — {self.role}"


class TeamMember(models.Model):
	name = models.CharField(max_length=150)
	poste = models.CharField(max_length=150)
	image = models.ImageField(upload_to="team/", blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Membre de l'équipe"
		verbose_name_plural = "Membres de l'équipe"
		ordering = ["id"]

	def __str__(self):
		return f"{self.name} — {self.poste}"
