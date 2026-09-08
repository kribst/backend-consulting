from django.db import migrations, models


class Migration(migrations.Migration):

	initial = True

	dependencies = []

	operations = [
		migrations.CreateModel(
			name="NewsletterSubscriber",
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
				("email", models.EmailField(max_length=254, unique=True)),
				("nom", models.CharField(blank=True, max_length=150)),
				(
					"statut",
					models.CharField(
						choices=[
							("actif", "Actif"),
							("desabonne", "Désabonné"),
						],
						default="actif",
						max_length=20,
					),
				),
				("source", models.CharField(blank=True, default="site", max_length=80)),
				("ip_address", models.GenericIPAddressField(blank=True, null=True)),
				("user_agent", models.CharField(blank=True, max_length=255)),
				("subscribed_at", models.DateTimeField(auto_now_add=True)),
				("unsubscribed_at", models.DateTimeField(blank=True, null=True)),
			],
			options={
				"ordering": ["-subscribed_at"],
			},
		),
	]
