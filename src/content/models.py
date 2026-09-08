from django.db import models


class SiteContent(models.Model):
	company = models.JSONField(default=dict)
	services = models.JSONField(default=list)
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
