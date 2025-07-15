# WhatsApp Bot Configuration Example
# Copy this to your main Django settings.py or create a separate config file

# Method 1: Direct Django Settings Configuration
# Add these to your main Django settings.py file:

# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN = 'EAFYi1HZB6eFQBPDpuWeyzIoTVGKMTj9JvZCXxsHwjmu5QYRR0EdN62EfpjkoQKSOZATJXA1m2bF5eAhkZAi9NXsZAp0YG0KFZCoOiWUcUBARAKbs8LhepWFxCKKcmjT3wmXzII7uDZBZBMFh8gX0roBqzybYfjFuMr9mpYLTqoxZAZCqivvYfWDhnouqHZCj9T82TIghQZDZD'
WHATSAPP_PHONE_NUMBER_ID = '651347521403933'
WHATSAPP_BUSINESS_ACCOUNT_ID = '1254335423034309'  # Optional, for reference
WHATSAPP_WEBHOOK_VERIFY_TOKEN = 'your_custom_verify_token_here'  # Set a secure token
WHATSAPP_WEBHOOK_SECRET = 'your_webhook_secret_here'  # Set a secure secret
WHATSAPP_API_VERSION = 'v18.0'
WHATSAPP_BASE_URL = 'https://graph.facebook.com'

# Method 2: Plugin-specific Configuration
# Add this to your main Django settings.py file:

PLUGIN_CONFIGS = {
    'care_whatsapp_bot': {
        'WHATSAPP_ACCESS_TOKEN': 'EAFYi1HZB6eFQBPDpuWeyzIoTVGKMTj9JvZCXxsHwjmu5QYRR0EdN62EfpjkoQKSOZATJXA1m2bF5eAhkZAi9NXsZAp0YG0KFZCoOiWUcUBARAKbs8LhepWFxCKKcmjT3wmXzII7uDZBZBMFh8gX0roBqzybYfjFuMr9mpYLTqoxZAZCqivvYfWDhnouqHZCj9T82TIghQZDZD',
        'WHATSAPP_PHONE_NUMBER_ID': '651347521403933',
        'WHATSAPP_WEBHOOK_VERIFY_TOKEN': 'your_custom_verify_token_here',
        'WHATSAPP_WEBHOOK_SECRET': 'your_webhook_secret_here',
        'WHATSAPP_API_VERSION': 'v18.0',
        'WHATSAPP_BASE_URL': 'https://graph.facebook.com',
        # Optional: Override other settings
        'BOT_NAME': 'CARE Assistant',
        'SESSION_TIMEOUT_MINUTES': 30,
        'RATE_LIMIT_MESSAGES_PER_MINUTE': 10,
    }
}

# Method 3: Environment Variables
# Set these in your environment or .env file:

# WHATSAPP_ACCESS_TOKEN=EAFYi1HZB6eFQBPDpuWeyzIoTVGKMTj9JvZCXxsHwjmu5QYRR0EdN62EfpjkoQKSOZATJXA1m2bF5eAhkZAi9NXsZAp0YG0KFZCoOiWUcUBARAKbs8LhepWFxCKKcmjT3wmXzII7uDZBZBMFh8gX0roBqzybYfjFuMr9mpYLTqoxZAZCqivvYfWDhnouqHZCj9T82TIghQZDZD
# WHATSAPP_PHONE_NUMBER_ID=651347521403933
# WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_custom_verify_token_here
# WHATSAPP_WEBHOOK_SECRET=your_webhook_secret_here

# Security Notes:
# 1. Never commit real credentials to version control
# 2. Use environment variables in production
# 3. Set strong, unique values for WEBHOOK_VERIFY_TOKEN and WEBHOOK_SECRET
# 4. The access token provided has limited lifetime - you may need to refresh it

# Required Settings:
# - WHATSAPP_ACCESS_TOKEN: Your WhatsApp Business API access token
# - WHATSAPP_PHONE_NUMBER_ID: Your WhatsApp Business phone number ID
# - WHATSAPP_WEBHOOK_VERIFY_TOKEN: Token for webhook verification
# - WHATSAPP_WEBHOOK_SECRET: Secret for webhook signature validation

# Next Steps:
# 1. Choose one of the configuration methods above
# 2. Set secure values for WEBHOOK_VERIFY_TOKEN and WEBHOOK_SECRET
# 3. Add the configuration to your main Django settings
# 4. Run migrations: python manage.py migrate
# 5. Test the configuration with: python manage.py test care_whatsapp_bot