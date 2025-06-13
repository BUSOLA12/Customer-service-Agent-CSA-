# WhatsApp CSA Project

## Overview

The WhatsApp CSA Project is a Django-based application designed to streamline customer interactions for real estate businesses. It integrates WhatsApp messaging, property management, and customer interaction tracking to provide a seamless experience for both customers and agents.

## Features

- **Property Management**: Add, update, and manage property listings with details like price, location, bedrooms, bathrooms, and availability.
- **Customer Interaction Tracking**: Log customer inquiries, preferences, and interactions for better service.
- **WhatsApp Integration**: Automatically handle customer messages via WhatsApp, including property inquiries, budget sharing, and feedback.
- **AI-Powered Intent Classification**: Use Google Gemini Studio to classify customer intents and respond accordingly.
- **Property Recommendations**: Suggest properties based on customer budget and preferences.
- **Webhook Integration**: Send property data to external services via webhooks.
- **Media Handling**: Manage property images and send media messages via WhatsApp.

## Technologies Used

- **Backend**: Django
- **Database**: SQLite
- **API**: Django REST Framework
- **AI Integration**: Google Gemini Studio
- **Messaging**: WhatsApp Business API
- **Cloud Integration**: Make.com Webhooks

## Setup Instructions

### Prerequisites

1. Python 3.8 or higher
2. Django 5.1.7
3. Virtual environment tool (e.g., `venv` or `virtualenv`)
4. WhatsApp Business API credentials
5. Google Cloud service account credentials

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/WhatsApp_CSA.git
   cd WhatsApp_CSA
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   - Create a `.env` file in the project root.
   - Add the required variables (refer to `.env` file in the project).

5. Apply migrations:

   ```bash
   python manage.py migrate
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Media Configuration

Ensure the `MEDIA_ROOT` directory exists for storing uploaded images:

```bash
mkdir media
```

### WhatsApp Webhook Configuration

Set up the webhook URL in your WhatsApp Business API settings to point to:

```
https://<your-domain>/webhook/
```

## Usage

### Admin Panel

Access the admin panel to manage properties:

```
http://127.0.0.1:8000/admin/
```

### WhatsApp Integration

Customers can interact with the system via WhatsApp. The application will:

- Classify intents (e.g., property inquiry, budget sharing).
- Respond with property details or recommendations.
- Log interactions for future reference.

### API Endpoints

- **Property List**: `/properties/`
  - Retrieve all property listings.
  - Example:
    ```bash
    curl http://127.0.0.1:8000/properties/
    ```

## Logging

Logs are stored in `app.log` for debugging and monitoring.

## Contributing

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature description"
   ```
4. Push to your fork:
   ```bash
   git push origin feature-name
   ```
5. Create a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or support, contact:

- **Email**: support@yourdomain.com
- **WhatsApp**: [WhatsApp Channel](https://whatsapp.com/channel/your_channel_id)
- **Instagram**: [Instagram Account](https://instagram.com/your_account)
