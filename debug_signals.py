#!/usr/bin/env python
"""
Debug script to test WhatsApp notification signals
Run this in your CARE Django environment to diagnose signal issues
"""

import os
import sys
import django
from django.conf import settings

def setup_django():
    """Setup Django environment"""
    # Add your CARE project path here
    # sys.path.append('/path/to/your/care/project')
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    django.setup()

def test_signal_registration():
    """Test if signals are properly registered"""
    print("🔍 Testing Signal Registration")
    print("=" * 50)
    
    try:
        from django.db.models.signals import post_save, pre_save
        from care.emr.models.scheduling.booking import TokenBooking
        
        # Check if our signals are connected
        post_save_receivers = post_save._live_receivers(sender=TokenBooking)
        pre_save_receivers = pre_save._live_receivers(sender=TokenBooking)
        
        print(f"📊 TokenBooking post_save receivers: {len(post_save_receivers)}")
        print(f"📊 TokenBooking pre_save receivers: {len(pre_save_receivers)}")
        
        # Check for our specific signal handlers
        our_handlers = []
        for receiver in post_save_receivers:
            if hasattr(receiver, '__name__'):
                print(f"   - {receiver.__name__}")
                if 'appointment_notification_handler' in receiver.__name__:
                    our_handlers.append(receiver.__name__)
        
        for receiver in pre_save_receivers:
            if hasattr(receiver, '__name__'):
                print(f"   - {receiver.__name__}")
                if 'store_original_appointment_data' in receiver.__name__:
                    our_handlers.append(receiver.__name__)
        
        if our_handlers:
            print(f"✅ Found our signal handlers: {our_handlers}")
        else:
            print("❌ Our signal handlers NOT found!")
            
    except Exception as e:
        print(f"❌ Error checking signal registration: {e}")

def test_app_installation():
    """Test if the WhatsApp bot app is properly installed"""
    print("\n🔍 Testing App Installation")
    print("=" * 50)
    
    try:
        installed_apps = settings.INSTALLED_APPS
        whatsapp_app_installed = any('care_whatsapp_bot' in app for app in installed_apps)
        
        print(f"📱 WhatsApp bot app installed: {whatsapp_app_installed}")
        
        if whatsapp_app_installed:
            print("✅ care_whatsapp_bot found in INSTALLED_APPS")
        else:
            print("❌ care_whatsapp_bot NOT found in INSTALLED_APPS")
            print("💡 Add 'care_whatsapp_bot' to your INSTALLED_APPS in settings")
            
        # Check plugin configs
        plugin_configs = getattr(settings, 'PLUGIN_CONFIGS', {})
        whatsapp_config = plugin_configs.get('care_whatsapp_bot', {})
        
        print(f"⚙️  Plugin config found: {bool(whatsapp_config)}")
        if whatsapp_config:
            print(f"   - Config keys: {list(whatsapp_config.keys())}")
            
    except Exception as e:
        print(f"❌ Error checking app installation: {e}")

def test_model_import():
    """Test if TokenBooking model can be imported"""
    print("\n🔍 Testing Model Import")
    print("=" * 50)
    
    try:
        from care.emr.models.scheduling.booking import TokenBooking
        print("✅ TokenBooking model imported successfully")
        
        # Test model access
        count = TokenBooking.objects.count()
        print(f"📊 Total TokenBooking records: {count}")
        
    except Exception as e:
        print(f"❌ Error importing TokenBooking: {e}")

def test_whatsapp_provider():
    """Test WhatsApp provider configuration"""
    print("\n🔍 Testing WhatsApp Provider")
    print("=" * 50)
    
    try:
        from care_whatsapp_bot.settings import plugin_settings
        
        access_token = getattr(plugin_settings, 'WHATSAPP_ACCESS_TOKEN', None)
        phone_number_id = getattr(plugin_settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        
        print(f"🔑 Access token configured: {bool(access_token)}")
        print(f"📱 Phone number ID configured: {bool(phone_number_id)}")
        
        if access_token and phone_number_id:
            print("✅ WhatsApp credentials are configured")
        else:
            print("❌ WhatsApp credentials missing!")
            print("💡 Configure WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID")
            
    except Exception as e:
        print(f"❌ Error testing WhatsApp provider: {e}")

def create_test_appointment():
    """Create a test appointment to trigger signals"""
    print("\n🔍 Creating Test Appointment")
    print("=" * 50)
    
    try:
        from care.emr.models.scheduling.booking import TokenBooking
        from care.emr.models.scheduling.slot import TokenSlot
        from care.users.models import User
        from datetime import datetime, timedelta
        
        print("⚠️  This will create a test appointment in your database!")
        response = input("Continue? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Test appointment creation cancelled")
            return
            
        # This is just a template - you'll need to adjust based on your actual model structure
        print("💡 You'll need to manually create a test appointment through CARE's interface")
        print("   and watch the logs for signal firing")
        
    except Exception as e:
        print(f"❌ Error in test appointment creation: {e}")

def main():
    """Main diagnostic function"""
    print("🏥 CARE WhatsApp Bot - Signal Diagnostics")
    print("=" * 60)
    
    try:
        setup_django()
        print("✅ Django environment setup complete")
    except Exception as e:
        print(f"❌ Failed to setup Django: {e}")
        print("💡 Make sure you're running this from your CARE project directory")
        print("💡 Update the Django settings module path in this script")
        return
    
    test_app_installation()
    test_model_import()
    test_signal_registration()
    test_whatsapp_provider()
    
    print("\n🔧 TROUBLESHOOTING STEPS:")
    print("=" * 60)
    print("1. Ensure 'care_whatsapp_bot' is in INSTALLED_APPS")
    print("2. Configure WhatsApp credentials in plugin settings")
    print("3. Restart Django server after adding the app")
    print("4. Check Django logs when creating appointments")
    print("5. Verify TokenBooking model structure matches expectations")
    
    print("\n📝 LOG MONITORING:")
    print("Add this to your Django logging config:")
    print("""
LOGGING = {
    'loggers': {
        'care_whatsapp_bot': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
""")

if __name__ == "__main__":
    main()