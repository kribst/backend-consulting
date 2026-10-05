from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0011_service_image_upload_directory"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actualite",
            name="image",
            field=models.ImageField(blank=True, upload_to="images/actualites/"),
        ),
    ]
