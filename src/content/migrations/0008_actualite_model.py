from django.db import migrations, models


def copy_actualites_to_model(apps, schema_editor):
    SiteContent = apps.get_model("content", "SiteContent")
    Actualite = apps.get_model("content", "Actualite")
    database = schema_editor.connection.alias

    for site_content in SiteContent.objects.using(database).all():
        items = site_content.actualites if isinstance(site_content.actualites, list) else []
        for position, item in enumerate(items):
            if not isinstance(item, dict) or not item.get("slug"):
                continue
            Actualite.objects.using(database).update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item.get("title", ""),
                    "category": item.get("category", ""),
                    "datePublication": item.get("datePublication") or "2000-01-01",
                    "heurePublication": item.get("heurePublication") or "00:00",
                    "image": item.get("image", ""),
                    "imageAlt": item.get("imageAlt", ""),
                    "content": item.get("content", []),
                    "position": position,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0007_sitecontent_actualites"),
    ]

    operations = [
        migrations.CreateModel(
            name="Actualite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=200, unique=True)),
                ("title", models.CharField(max_length=255)),
                ("category", models.CharField(max_length=120)),
                ("datePublication", models.DateField()),
                ("heurePublication", models.TimeField()),
                ("image", models.CharField(max_length=500)),
                ("imageAlt", models.CharField(max_length=255)),
                ("content", models.JSONField(default=list)),
                ("position", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Actualité",
                "verbose_name_plural": "Actualités",
                "ordering": ["position", "id"],
            },
        ),
        migrations.RunPython(copy_actualites_to_model, migrations.RunPython.noop),
    ]
