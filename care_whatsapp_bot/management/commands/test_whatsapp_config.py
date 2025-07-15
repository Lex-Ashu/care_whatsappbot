from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json
from care_whatsapp_bot.settings import plugin_settings
from care_whatsapp_bot.im_wrapper.whatsapp import WhatsAppProvider


class Command(BaseCommand):
    help = 'Test WhatsApp configuration and API connectivity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-test',
            action='store_true',
            help='Send a test message to verify configuration',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number to send test message to (format: +1234567890)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Testing WhatsApp Configuration...'))
        
        # Check required settings
        required_settings = [
            'WHATSAPP_ACCESS_TOKEN',
            'WHATSAPP_PHONE_NUMBER_ID',
            'WHATSAPP_WEBHOOK_VERIFY_TOKEN',
            'WHATSAPP_WEBHOOK_SECRET'
        ]
        
        missing_settings = []
        for setting in required_settings:
            try:
                value = getattr(plugin_settings, setting)
                if not value:
                    missing_settings.append(setting)
                else:
                    # Mask sensitive values for display
                    if 'TOKEN' in setting or 'SECRET' in setting:
                        display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                    else:
                        display_value = value
                    self.stdout.write(f"✅ {setting}: {display_value}")
            except Exception as e:
                missing_settings.append(setting)
                self.stdout.write(self.style.ERROR(f"❌ {setting}: Missing or invalid"))
        
        if missing_settings:
            self.stdout.write(self.style.ERROR(f"\n❌ Missing required settings: {', '.join(missing_settings)}"))
            self.stdout.write("\n📝 Configuration Help:")
            self.stdout.write("1. Check care_whatsapp_bot/whatsapp_config_example.py for setup instructions")
            self.stdout.write("2. Set credentials in Django settings or environment variables")
            self.stdout.write("3. Ensure WHATSAPP_WEBHOOK_VERIFY_TOKEN and WHATSAPP_WEBHOOK_SECRET are set to secure values")
            return
        
        # Test API connectivity
        self.stdout.write("\n🌐 Testing WhatsApp API connectivity...")
        try:
            provider = WhatsAppProvider({
                'access_token': plugin_settings.WHATSAPP_ACCESS_TOKEN,
                'phone_number_id': plugin_settings.WHATSAPP_PHONE_NUMBER_ID
            })
            
            # Test API endpoint
            url = f"{plugin_settings.WHATSAPP_BASE_URL}/{plugin_settings.WHATSAPP_API_VERSION}/{plugin_settings.WHATSAPP_PHONE_NUMBER_ID}"
            headers = {
                'Authorization': f'Bearer {plugin_settings.WHATSAPP_ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✅ WhatsApp API connection successful"))
                data = response.json()
                if 'display_phone_number' in data:
                    self.stdout.write(f"📱 Phone Number: {data['display_phone_number']}")
                if 'verified_name' in data:
                    self.stdout.write(f"🏢 Business Name: {data['verified_name']}")
            else:
                self.stdout.write(self.style.ERROR(f"❌ API connection failed: {response.status_code}"))
                self.stdout.write(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Network error: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Configuration error: {str(e)}"))
        
        # Send test message if requested
        if options['send_test']:
            if not options['phone']:
                self.stdout.write(self.style.ERROR("\n❌ Please provide --phone argument for test message"))
                return
                
            self.stdout.write(f"\n📤 Sending test message to {options['phone']}...")
            try:
                provider = WhatsAppProvider({
                    'access_token': plugin_settings.WHATSAPP_ACCESS_TOKEN,
                    'phone_number_id': plugin_settings.WHATSAPP_PHONE_NUMBER_ID
                })
                
                result = provider.send_message(
                    to=options['phone'],
                    message="🤖 Test message from CARE WhatsApp Bot! Configuration is working correctly."
                )
                
                if result.get('success'):
                    self.stdout.write(self.style.SUCCESS("✅ Test message sent successfully!"))
                    if 'message_id' in result:
                        self.stdout.write(f"📧 Message ID: {result['message_id']}")
                else:
                    self.stdout.write(self.style.ERROR(f"❌ Failed to send test message: {result.get('error', 'Unknown error')}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error sending test message: {str(e)}"))
        
        self.stdout.write("\n🎉 Configuration test completed!")
        self.stdout.write("\n📚 Next steps:")
        self.stdout.write("1. Set up webhook URL in Meta Developer Console")
        self.stdout.write("2. Configure webhook verify token in Meta Console")
        self.stdout.write("3. Test webhook with: python manage.py test care_whatsapp_bot.tests")
        self.stdout.write("4. Monitor logs for any issues")