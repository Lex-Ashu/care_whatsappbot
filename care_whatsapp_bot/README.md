# CARE WhatsApp Bot Plugin

A comprehensive WhatsApp bot integration for the CARE platform, enabling patients and hospital staff to interact with the system through WhatsApp messages.

## Features

### For Patients
- 🔐 **Secure Authentication**: OTP-based login system
- 📋 **Medical Records**: Access to personal medical history
- 💊 **Medication Information**: View current and past medications
- 📅 **Appointment Management**: Check upcoming appointments
- 🏥 **Procedure History**: Access to medical procedures
- 📱 **Real-time Notifications**: Appointment reminders, medication alerts

### For Hospital Staff
- 👥 **Patient Search**: Find patients by name or phone number
- 📊 **Patient Information**: Quick access to patient data
- 📅 **Appointment Scheduling**: Schedule appointments via WhatsApp
- 🔒 **Privacy Controls**: Automatic data filtering and masking

### System Features
- 🔄 **Async Processing**: Celery-based message processing
- 📈 **Analytics**: Usage tracking and reporting
- 🛡️ **Security**: Webhook signature validation, rate limiting
- 🗄️ **Data Management**: Automatic cleanup and archiving
- 🔧 **Admin Interface**: Django admin integration

## Installation

### Prerequisites

1. **CARE Platform**: This plugin requires a running CARE instance
2. **WhatsApp Business API**: Access to WhatsApp Business API
3. **Redis**: For caching and Celery task queue
4. **Celery**: For async task processing

### Step 1: Install Dependencies

```bash
# Install plugin dependencies
pip install -r requirements.txt
```

### Step 2: Configure Django Settings

Add the plugin to your CARE settings:

```python
# settings.py

INSTALLED_APPS = [
    # ... existing apps
    'care_whatsapp_bot',
]

# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN = 'your_whatsapp_access_token'
WHATSAPP_PHONE_NUMBER_ID = 'your_phone_number_id'
WHATSAPP_WEBHOOK_VERIFY_TOKEN = 'your_verify_token'
WHATSAPP_WEBHOOK_SECRET = 'your_webhook_secret'
WHATSAPP_API_VERSION = 'v18.0'
WHATSAPP_BASE_URL = 'https://graph.facebook.com'

# Bot Configuration
WHATSAPP_BOT_NAME = 'CARE Assistant'
WHATSAPP_BOT_WELCOME_MESSAGE = 'Welcome to CARE! Type "help" for available commands.'
WHATSAPP_SESSION_TIMEOUT_HOURS = 24
WHATSAPP_MAX_MESSAGE_LENGTH = 4096

# Celery Configuration (if not already configured)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Cache Configuration (if not already configured)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Step 3: Update URL Configuration

WhatsApp bot URLs are automatically included via the plugin's URL configuration.

### Step 4: Run Migrations

```bash
python manage.py migrate care_whatsapp_bot
```

### Step 5: Set Up WhatsApp Webhook

```bash
# Set up webhook (replace with your actual values)
python manage.py setup_whatsapp_webhook \
    --webhook-url https://yourdomain.com/api/v1/whatsapp/webhook/ \
    --verify-token your_verify_token \
    --access-token your_access_token \
    --phone-number-id your_phone_number_id

# Test with a message
python manage.py send_test_message +1234567890
```

### Step 6: Start Celery Workers

```bash
# Start Celery worker
celery -A care worker -l info

# Start Celery beat (for scheduled tasks)
celery -A care beat -l info
```

## Configuration

### Environment Variables

For production, use environment variables:

```bash
export WHATSAPP_ACCESS_TOKEN="your_access_token"
export WHATSAPP_PHONE_NUMBER_ID="your_phone_number_id"
export WHATSAPP_WEBHOOK_SECRET="your_webhook_secret"
export WHATSAPP_WEBHOOK_VERIFY_TOKEN="your_verify_token"
```

### WhatsApp Business API Setup

1. **Create a WhatsApp Business Account**
2. **Set up a WhatsApp Business API application**
3. **Get your access token and phone number ID**
4. **Configure webhook URL** pointing to your CARE instance

### Development Setup with ngrok

For local development:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Expose local server
ngrok http 8000

# Use the HTTPS URL provided by ngrok as your webhook URL
```

## Usage

### Patient Commands

- `login` - Start authentication process
- `help` - Show available commands
- `menu` - Show main menu
- `get records` - View medical records
- `get medications` - View medications
- `get appointments` - View appointments
- `get procedures` - View procedures
- `logout` - End session

### Staff Commands

- `login` - Start authentication process
- `patient search <name>` - Search for patients
- `patient info <phone>` - Get patient information
- `schedule appointment <details>` - Schedule appointment
- `help` - Show available commands
- `logout` - End session

### Example Conversation

```
User: login
Bot: 🔐 Please enter your phone number to receive an OTP.

User: +1234567890
Bot: 📱 OTP sent to +1234567890. Please enter the 6-digit code.

User: 123456
Bot: ✅ Login successful! Welcome to CARE.

User: help
Bot: 📋 Available Commands:
• get records - View your medical records
• get medications - View your medications
• get appointments - View your appointments
• logout - End session

User: get appointments
Bot: 📅 Your Upcoming Appointments:

🏥 Dr. Smith - Cardiology
📅 Tomorrow, 2:00 PM
📍 Room 205, Main Building
```

## API Endpoints

### Webhook Endpoints

- `GET /api/v1/whatsapp/webhook/` - Webhook verification
- `POST /api/v1/whatsapp/webhook/` - Incoming message processing

### Utility Endpoints

- `GET /api/v1/whatsapp/health/` - Health check
- `POST /api/v1/whatsapp/send_test_message/` - Send test message (development only)

## Administration

### Django Admin Interface

The plugin provides comprehensive admin interfaces for:

- **WhatsApp Sessions**: Monitor active user sessions
- **WhatsApp Messages**: View message history and processing status
- **WhatsApp Commands**: Track command execution
- **WhatsApp Notifications**: Manage scheduled notifications

### Monitoring

#### Health Check

```bash
curl https://yourdomain.com/api/v1/whatsapp/health/
```

#### Session Management

```python
# Get active sessions
from care_whatsapp_bot.models.whatsapp import WhatsAppSession
active_sessions = WhatsAppSession.objects.filter(is_active=True)

# Clean up expired sessions
from care_whatsapp_bot.tasks import cleanup_whatsapp_data
cleanup_whatsapp_data.delay()
```

## Development

### Running Tests

```bash
# Run all tests
python manage.py test care_whatsapp_bot

# Run with coverage
pytest --cov=care_whatsapp_bot

# Run specific test
python manage.py test care_whatsapp_bot.tests.WhatsAppModelTests
```

### Code Quality

```bash
# Format code
black care_whatsapp_bot/

# Check linting
flake8 care_whatsapp_bot/

# Type checking
mypy care_whatsapp_bot/
```

### Adding New Handlers

1. Create a new handler in `handlers/`
2. Inherit from `BaseHandler`
3. Implement required methods
4. Register in `message_router.py`

```python
# handlers/custom_handler.py
from .base import BaseHandler

class CustomHandler(BaseHandler):
    def can_handle(self, message, session):
        return message.content.startswith('custom')
    
    def handle(self, message, session):
        return "Custom response"
```

## Security

### Webhook Security

- **Signature Validation**: All incoming webhooks are validated using HMAC-SHA256
- **Token Verification**: Webhook verification tokens are required
- **Rate Limiting**: Built-in rate limiting for message processing

### Data Privacy

- **Session Management**: Automatic session expiration
- **Data Masking**: Sensitive data is automatically masked in logs
- **Access Controls**: Role-based access to patient data

### Best Practices

1. **Use HTTPS**: Always use HTTPS for webhook URLs
2. **Rotate Tokens**: Regularly rotate access tokens and secrets
3. **Monitor Logs**: Set up log monitoring for security events
4. **Backup Data**: Regular backups of WhatsApp session data

## Troubleshooting

### Common Issues

#### Webhook Not Receiving Messages

1. Check webhook URL is accessible
2. Verify webhook verification token
3. Check WhatsApp Business API configuration
4. Review server logs for errors

#### Messages Not Being Processed

1. Check Celery workers are running
2. Verify Redis connection
3. Check task queue for failed tasks
4. Review message processing logs

#### Authentication Issues

1. Verify OTP service configuration
2. Check phone number format
3. Review authentication logs
4. Verify user permissions

### Logging

```python
# Enable debug logging
LOGGING = {
    'loggers': {
        'care_whatsapp_bot': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Contact the CARE development team
- Check the CARE documentation

## Changelog

### Version 1.0.0

- Initial release
- Basic WhatsApp integration
- Patient and staff authentication
- Message routing and handling
- Admin interface
- Comprehensive test suite