from django.db import migrations


def create_testimonials(apps, schema_editor):
    Testimonial = apps.get_model("content", "Testimonial")
    testimonials = [
        {
            "name": "Directeur général",
            "role": "PME à Yaoundé",
            "quote": "FALKCO nous a aidés à clarifier nos priorités de gestion et à structurer un plan d'action réaliste.",
        },
        {
            "name": "Porteuse de projet",
            "role": "Entrepreneuriat",
            "quote": "L'accompagnement a été sérieux, progressif et adapté. Nous avons gagné en visibilité.",
        },
        {
            "name": "Responsable formation",
            "role": "Organisation professionnelle",
            "quote": "La formation était pratique, claire et directement liée aux besoins de nos équipes.",
        },
    ]
    for item in testimonials:
        Testimonial.objects.create(**item)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0002_testimonial"),
    ]

    operations = [
        migrations.RunPython(create_testimonials, reverse_code=migrations.RunPython.noop),
    ]
