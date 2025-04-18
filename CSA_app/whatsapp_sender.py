import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_whatsapp_message(recipient_phone, message_text, media_url=None):

    try:
        headers = {
            'Authorization': f'Bearer {
                settings.WHATSAPP_ACCESS_TOKEN
            }',
            'Content-Type': 'application/json'
        }

        if recipient_phone.startswith('+'):
            recipient_phone = recipient_phone[1:]


        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "recipient_type": "individual"
        }

        if media_url:
            payload["type"] = "image"
            payload["image"] = {
                "link": media_url
            }

            if message_text:
                payload["image"]["caption"] = message_text
        else:

            payload["type"] = "text"
            payload["text"] = {
                "body": message_text
            }
        
        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info(f"WhatsApp message sent successfully to {recipient_phone}")
            return True
        else:
            logger.error(f"Failed to send WhatsApp message : {response.text}")

    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return False
    

def send_template_message(recipient_phone, template_name, language_code="en_US", components=None):

    try:
        headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-type': 'application/json'
        }

        if recipient_phone.startswith('+'):
            recipient_phone = recipient_phone[1:]

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }


        if components:
            payload["template"]["components"] = components


        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info(f"WhatsApp template message sent successfully to {recipient_phone}")
            return True
        
        else:
            logger.error(f"Failed to send WhatsApp template message: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error sending WhatsApp template message: {str(e)}")
        return False