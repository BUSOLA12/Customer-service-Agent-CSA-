# Generated by Django 5.1.7 on 2025-03-26 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CSA_app', '0002_alter_customer_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='property_identifier',
            field=models.CharField(blank=True, editable=False, max_length=255, unique=True),
        ),
    ]
