from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from .whatsapp_handler import process_whatsapp_message
import logging
logger = logging.getLogger(__name__)

# Create your views here.



from django.views.decorators.csrf import csrf_exempt

# Define the verify token for WhatsApp webhook verification
verify = "EAANQ85Ec7NMBO17DU4AvAWnbhnNn49t7e3lBOuKmMnS1q1NwgtvxE1WbrKUZAEmLhT4WpBugY5ZCnnHAK9fwAsIFh3grZCyXDZCC9YLU4ZAGzYhS3rjWwBNh6ulKZC7hPB5S7YJtM6TkY7iyqafRPZCBwp7QnQdtrBqp4WievmEi0E4A8Fhf5ti7hOZC4SQ1xZAQgwKG9LN8boz8hhkGymqSAOmXsaSQZD"

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        try:
            # Load the incoming data from WhatsApp
            data = json.loads(request.body)
            logging.info(f"(view)Received WhatsApp Data: {json.dumps(data, indent=2)}")

            # Extract the message data
            
            if 'entry' in data and data['entry']:
                changes = data['entry'][0].get('changes', [])
                if changes and 'value' in changes[0] and 'messages' in changes[0]['value']:
                    message = changes[0]['value']['messages'][0]
                    sender = message['from']
                    message_body = message['text']['body'] if 'text' in message else None
                    
                    # Process the message
                    process_whatsapp_message(sender, message_body, message)
            # Return a success response
            return HttpResponse(status=200)
            
        except Exception as e:
            logging.error(f"(View.py)Error processing WhatsApp message: {str(e)}")
            return HttpResponse(status=500)

    elif request.method == 'GET':
        # Handle WhatsApp webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        logging.info(f"(view)Verification request received with mode: {mode}, token: {token}")

        # Check if the mode and token match
        if mode == 'subscribe' and token == verify:
            logging.info("Webhook verified successfully")
            return HttpResponse(challenge, status=200)
        else:
            logging.error(f"(view)Verification failed. Invalid token: {token}")
            return HttpResponse(status=403)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import Property
from .serializers import PropertySerializer

class PropertyListAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        properties = Property.objects.all().order_by('-created_at')
        serializer = PropertySerializer(properties, many=True)
        logging.info(f"(view)Property data: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)
