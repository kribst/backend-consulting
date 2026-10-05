from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0010_alter_actualite_image_alter_service_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="image",
            field=models.ImageField(blank=True, upload_to="images/services/"),
        ),
    ]
