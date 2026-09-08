from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		("newsletter", "0001_initial"),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name="NewsletterCampaign",
			fields=[
				(
					"id",
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name="ID",
					),
				),
				("sujet", models.CharField(max_length=255)),
				("message", models.TextField()),
				(
					"audience",
					models.CharField(
						choices=[
							("all", "Tous les abonnés"),
							("actifs", "Abonnés actifs uniquement"),
							("desabonnes", "Désabonnés uniquement"),
							("selection", "Sélection manuelle"),
						],
						default="actifs",
						max_length=20,
					),
				),
				(
					"statut",
					models.CharField(
						choices=[
							("brouillon", "Brouillon"),
							("envoyee", "Envoyée"),
							("echouee", "Échouée"),
						],
						default="brouillon",
						max_length=20,
					),
				),
				("destinataires_count", models.PositiveIntegerField(default=0)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("envoyee_at", models.DateTimeField(blank=True, null=True)),
				(
					"envoye_par",
					models.ForeignKey(
						blank=True,
						null=True,
						on_delete=models.SET_NULL,
						related_name="newsletter_campaigns",
						to=settings.AUTH_USER_MODEL,
					),
				),
			],
			options={
				"ordering": ["-created_at"],
			},
		),
	]
