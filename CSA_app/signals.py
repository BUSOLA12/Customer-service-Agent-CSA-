import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Property

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # Log messages will be saved to 'app.log'
    filemode='a'  # Append to the log file instead of overwriting
)

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Property)
def send_property_to_make(sender, instance, created, **kwargs):
    if created:
        make_webhook_url = 'https://hook.eu2.make.com/v8aqa65woci0j31chn5iv2kxrh5nqvd9'

        with open(instance.image.path, 'rb') as img_file:
            files = {
                'image': (instance.image.name, img_file, 'image/jpeg'),
            }

            data = {
                "title": str(instance.name),
                "description": str(instance.description),
                "price": str(instance.price),
                "location": str(instance.location),
                "image_url": str(instance.image_urls)
            }


            try:
                response = requests.post(make_webhook_url, data=data, files=files)
                response.raise_for_status()

            except requests.RequestException as e:
                logger.error(f"Error message from sending data to webhook: {str(e)}")


































