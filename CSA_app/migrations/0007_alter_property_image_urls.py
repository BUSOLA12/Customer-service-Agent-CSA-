# Generated by Django 5.1.7 on 2025-04-13 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("CSA_app", "0006_property_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="property",
            name="image_urls",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
