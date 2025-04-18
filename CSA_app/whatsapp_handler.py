from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini Studio
from django.conf import settings
import os
from .models import Customer, Property, Interaction
from .whatsapp_sender import send_whatsapp_message
import json
import re
import logging
from decimal import Decimal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # Log messages will be saved to 'app.log'
    filemode='a'  # Append to the log file instead of overwriting
)

logger = logging.getLogger(__name__)

# Set Google credentials
api_key = settings.GEMINI_API_KEY
# Initialize Gemini Studio LLM
llm = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-2.0-flash")

def create_chain(prompt_template):
    return prompt_template | llm

# Define the chat prompts
intent_classification_prompt = ChatPromptTemplate.from_template(
    """
    Classify the intent of the following customer message related to real estate:
    
    Customer message: {message}
    
    Possible intents:
    - property_inquiry (customer is asking about a specific property)
    - property_recommendation (customer is looking for property recommendations)
    - budget_sharing (customer is sharing their budget)
    - post_inspection_feedback (customer is providing feedback after an inspection)
    - payment_method (customer is asking about or sharing payment preferences)
    - general_query (any other general questions)
    
    Return only the intent name without any explanation.
    Pls stick to the instructions above strictly
    """
)

property_inquiry_prompt = ChatPromptTemplate.from_template(
    """
    Extract property details from the customer's message:
    
    Customer message: {message}
    
    Extract the following information if available:
    - Property identifier
    - name
    - Location preferences
    - Number of bedrooms
    - Budget 
    - Any other specific requirements
     

    Format the output as a valid JSON object **without any extra formatting like markdown or triple backticks**.

    Example:

    {{
        "Property_identifier: "#47237"
        "name": "bungalow",
        "Location": "express road",
        "Bedrooms": null **integer**,
        "Budget": null **float**,
        "Any_other_specific_requirements": null
    }}

    """
)

post_inspection_prompt = ChatPromptTemplate.from_template(
    """
    Determine if the customer's feedback after inspection is positive or negative:
    
    Customer message: {message}
    
    Return only "positive" or "negative" without any explanation.
    """
)

# Create Chains
intent_chain = intent_classification_prompt | llm
property_inquiry_chain = property_inquiry_prompt | llm
post_inspection_chain = post_inspection_prompt | llm

def process_whatsapp_message(sender_phone, message_text, full_message):
    customer, created = Customer.objects.get_or_create(phone_number=sender_phone)

    # if created:
    #     print(f"Customer with phone number {sender_phone} was created.")
    # else:
    #     print(f"Customer with phone number {sender_phone} already exists.")

    has_image = 'image' in full_message

    if not message_text and has_image:
        intent = "property_inquiry"
    else:
        intent_result = None
        try:
            intent_result = intent_chain.invoke({"message": message_text})
            # print(intent_result)  # Print the result for debugging
        except Exception as e:
            print(f"Error invoking chain: {e}")
        
        intent = intent_result.content
        logger.info(f"intent: {intent}")

    if intent == "property_inquiry":
        handle_property_inquiry(customer, message_text, has_image, full_message)
    elif intent == "budget_sharing":
        handle_budget_sharing(customer, message_text)
    elif intent == "post_inspection_feedback":
        handle_post_inspection_feedback(customer, message_text)
    elif intent == "payment_method":
        handle_payment_method(customer, message_text)
    else:
        handle_general_query(customer, message_text)





        


def handle_property_inquiry(customer, message_text, has_image, full_message):

    property_id = None

    if has_image:

        # later i might use image recognition or metadata, but now i'll use property_id

        if message_text:

            matches = re.findall(r"property\s+#?(\d+)", message_text, re.IGNORECASE)
            if matches:

                property_id = matches[0]
                print(property_id)

    if message_text:

        inquiry_details = property_inquiry_chain.invoke({"message": message_text})
        # print(inquiry_details)
        try:

            details_json = inquiry_details.content

            details_json = details_json.strip('```json\n').strip('```')

            logger.info(f"Successfully retrieved details_json: {details_json}")

            
            
            details_json = json.loads(details_json)

            logger.info(f"Successfully retrieved property_details: {details_json}")
            
            
            property_identifier = details_json.get("Property_identifier")
            
            logger.info(f"Successfully retrieved property_identifier: {property_identifier}")
            

            if "Budget" in details_json and details_json["Budget"]:

                try:
                    
                    budget_value = float(re.sub(r'[^\d.]', '', str(details_json["Budget"])))
                    
                    


                    logger.info(f"Successfully retrieved budget_value: %s", budget_value)

                    budget_value = Decimal(budget_value)
                    customer.budget = budget_value

                except Exception as e:

                    pass

            if "Location" in details_json or "Bedrooms" in details_json:

                preferences = customer.preferences or {}

                if "Location" in details_json:
                    preferences["Location"] = details_json["Location"]

                if "Bedrooms" in details_json:
                    preferences["Bedrooms"] = details_json["Bedrooms"]

                
                # logger.info(f"Successfully retrieved preferences: {preferences}")

                customer.preferences = preferences

            customer.save()
        except AttributeError as e:
    # Handles case where `inquiry_details.content` doesn't exist or isn't a valid attribute
            logger.error("Error: 'inquiry_details' object does not have a 'content' attribute.", exc_info=True)

        except json.JSONDecodeError as e:
            # Handles case where JSON string is improperly formatted
            logger.error("Error: Unable to decode JSON. Please check the format of 'details_json'.", exc_info=True)

        except TypeError as e:
            # Handles case where `details_json` is not a string
            logger.error("Error: 'details_json' is not a valid string.", exc_info=True)

        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)

    
    property_obj = None
    if property_identifier:
        try:
            

            property_obj = Property.objects.get(property_identifier=property_identifier)
            logger.info(f"Property location is: {property_obj.location}")


        except Exception as e:
            pass
            # logger.info(f"An error occured: {str(e)}")

        # except Property.DoesNotExist:
            
        #     logger.error(f"An unexpected error occurred: Property object does not exist")
    

    Interaction.objects.create(
        customer=customer,
        property=property_obj,
        Interaction_type="inquiry",
        notes=message_text
    )

    # interactions = Interaction.objects.get(customer=customer)

    # for interaction in interactions:

    #     logger.info(f"Interaction note is: {interaction.notes}")


    if property_obj:
        if property_obj.is_available:
            response = (
                
                f"Thank you for your interest in {property_obj.name}!"
                f"This property is available for viewing."
                f"Please call our agent at {settings.AGENT_PHONE_NUMBER} to schedule an inspection."
            )

        else:

            response = (
                    f"Thank you for your interest in {property_obj.name}!"
                    f"Unfortunately, this property is currently not available."
                    f"May I know your budget so i can recommend similar properties?"

            )
    else:

        response = (
            "Thank you for your interest in our properties. "
            "To help you better, could you please share your budget and preferred location? "
            "This will help us recommend suitable properties for you."
        )

    send_whatsapp_message(customer.phone_number, response)

def handle_budget_sharing(customer, message_text):
    
    budget_match = re.search(r'(\d[\d,.]*\s?[kKmM]?)', message_text)
    logger.info(f"Budget is: {budget_match.group(1)}")

    if budget_match:
        try:
            budget = float(re.sub(r'[^\d.]', '', budget_match.group(1)))
            logger.info(f"New Budget is: {budget}")

            customer.budget = budget
            customer.save()


            lower_range = budget * 0.8
            upper_range = budget * 1.2

            logger.info(f"lower_range: {lower_range}")
            logger.info(f"upper_range: {upper_range}")

            properties_below = Property.objects.filter(
                price__lt=budget,
                price__gte=lower_range,
                is_available=True
            ).order_by('-price')[:3]

            properties_above = Property.objects.filter(
                price__gt=budget,
                price__lte=upper_range,
                is_available=True
            ).order_by('price')[:3]

            recommended_properties = list(properties_below) + list(properties_above)

            logger.info(f"recommended_properties: {recommended_properties}")

            # Interaction.objects.create(
            # customer=customer,
            # Interaction_type="budget_sharing",
            # notes=message_text
            #     )

            if recommended_properties:
                response = "Based on your budget, here are some properties you might be interested in:\n\n"

                for prop in recommended_properties:
                    response += (
                        
                        f"- {prop.name}: {prop.bedrooms} bedroom(s) in {prop.location} "
                        f"for ${prop.price:,.2f}\n"
                                 )

                response += (
                    "\nFor more details, please follow our WhatsApp channel: "
                    f"{settings.WHATSAPP_CHANNEL_LINK}\n"
                    f"You can also check our Instagram: {settings.INSTAGRAM_LINK}"
                )
            else:
                response = (
                    "Thank you for sharing your budget. We don't have properties in that range at the moment. "
                    "Please join our WhatsApp channel for updates on new properties: "
                    f"{settings.WHATSAPP_CHANNEL_LINK}"
                )
        except ValueError:
            response = (
                "I couldn't recognize the budget amount. "
                "Please send your budget in numerical format, for example: 200000"
            )
    else:
        response = (
            "Thank you for your message. To help you find suitable properties, "
            "could you please share your budget in numerical format?"
        )
    send_whatsapp_message(customer.phone_number, response)

#     # if an error occur I might need to comment this out.
    

def handle_post_inspection_feedback(customer, message_text):

    sentiment = post_inspection_chain.invoke({"message": message_text})

    logger.info(f"sentiment: {sentiment}")

    sentiment = sentiment.content.strip().lower()

    logger.info(f"sentiment: {sentiment}")

    recent_interaction = Interaction.objects.filter(
        customer=customer,
        Interaction_type="inquiry"
    ).order_by('-timestamp').first()

    property_obj = recent_interaction.property if recent_interaction else None

    logger.info(f"property_obj location: {property_obj.location}")

    Interaction.objects.create(
        customer=customer,
        property=property_obj,
        Interaction_type="post_inspection",
        notes=f"Feedback: {message_text} (Sentiment: {sentiment})" 
    )

    if sentiment == "positive":
        response = (
            "Greate to hear you liked the property! Would you like to proceed with the application? "
            "Please let us know your preferred payment method and schedule. "
        )
    else:
        response = (
            "I'm sorry to hear the property didn't meet your expectations. "
            "Could you share what specific features you're looking for? "
            "This will help us find a better match for your needs. "
        )
    send_whatsapp_message(customer.phone_number, response)

def handle_payment_method(customer, message_text):

    recent_interaction = Interaction.objects.filter(
        customer=customer,
        Interaction_type="post_inspection"
    ).order_by('-timestamp').first()

    property_obj = recent_interaction.property if recent_interaction else None


    Interaction.objects.create(
        customer=customer,
        property=property_obj,
        Interaction_type="payment_info",
        notes=f"Payment info: {message_text}"
    )

    response = (
        "Thank you for sharing your payment information. Our agent will contact you shortly "
        "to guild you through the next steps in the application process. "
        "If you have any questions in the meantime, please don't hesitate to ask."
    )

    send_whatsapp_message(customer.phone_number, response)

def handle_general_query(customer, message_text):

    Interaction.objects.create(
        customer=customer,
        Interaction_type="genaral_query",
        notes=message_text
    )

    response = (
        "Thank you for your message. If you're looking for properties, "
        "please share your budget and preferences so we can help you find suitable options. "
        "You can also check our available listings on our WhatsApp channel: "
        f"{settings.WHATSAPP_CHANNEL_LINK} or Instagram: {settings.INSTAGRAM_LINK}"
    )

    send_whatsapp_message(customer.phone_number, response)