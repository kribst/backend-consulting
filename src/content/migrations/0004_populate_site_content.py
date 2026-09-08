from django.db import migrations


def create_default_site_content(apps, schema_editor):
    SiteContent = apps.get_model("content", "SiteContent")
    if SiteContent.objects.exists():
        return
    SiteContent.objects.create(
        statistics=[
            {"label": "Experts", "value": "6", "description": "profils mobilisables selon les missions"},
            {"label": "Clients satisfaits", "value": "39", "description": "organisations accompagnées avec rigueur"},
            {"label": "Missions réalisées", "value": "19", "description": "interventions structurées et documentées"},
            {"label": "Parcours formation", "value": "8", "description": "programmes adaptés aux équipes"},
        ]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0003_populate_testimonials"),
    ]

    operations = [
        migrations.RunPython(create_default_site_content, reverse_code=migrations.RunPython.noop),
    ]
