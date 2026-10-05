import json
from pathlib import Path

from django.db import migrations, models


def copy_services_to_model(apps, schema_editor):
    SiteContent = apps.get_model("content", "SiteContent")
    Service = apps.get_model("content", "Service")
    database = schema_editor.connection.alias
    fixture_path = Path(__file__).resolve().parent.parent / "default_services.json"
    defaults = json.loads(fixture_path.read_text(encoding="utf-8"))

    for site_content in SiteContent.objects.using(database).all():
        items = site_content.services if isinstance(site_content.services, list) and site_content.services else defaults
        for position, item in enumerate(items):
            if not isinstance(item, dict) or not item.get("slug"):
                continue
            Service.objects.using(database).update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item.get("title", ""),
                    "icon": item.get("icon", ""),
                    "summary": item.get("summary", ""),
                    "description": item.get("description", ""),
                    "image": item.get("image", ""),
                    "imageAlt": item.get("imageAlt", ""),
                    "keyPoints": item.get("keyPoints", []),
                    "includes": item.get("includes", []),
                    "audience": item.get("audience", []),
                    "benefits": item.get("benefits", []),
                    "useCases": item.get("useCases", []),
                    "process": item.get("process", []),
                    "relatedSlugs": item.get("relatedSlugs", []),
                    "position": position,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0008_actualite_model"),
    ]

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("slug", models.CharField(max_length=255, unique=True)),
                ("icon", models.CharField(max_length=100)),
                ("summary", models.TextField()),
                ("description", models.TextField()),
                ("image", models.CharField(max_length=500)),
                ("imageAlt", models.CharField(max_length=255)),
                ("keyPoints", models.JSONField(default=list)),
                ("includes", models.JSONField(default=list)),
                ("audience", models.JSONField(default=list)),
                ("benefits", models.JSONField(default=list)),
                ("useCases", models.JSONField(default=list)),
                ("process", models.JSONField(default=list)),
                ("relatedSlugs", models.JSONField(default=list)),
                ("position", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Service",
                "verbose_name_plural": "Services",
                "ordering": ["position", "id"],
            },
        ),
        migrations.RunPython(copy_services_to_model, migrations.RunPython.noop),
    ]
