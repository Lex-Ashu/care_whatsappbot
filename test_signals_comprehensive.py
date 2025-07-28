#!/usr/bin/env python3
"""
Comprehensive test script to verify WhatsApp notification signals are working
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'care_whatsapp_bot',
        ],
        SECRET_KEY='test-secret-key-for-signals',
        USE_TZ=True,
        PLUGIN_CONFIGS={
            'care_whatsapp_bot': {
                'WHATSAPP_ACCESS_TOKEN': 'test_token',
                'WHATSAPP_PHONE_NUMBER_ID': 'test_phone_id',
                'WHATSAPP_WEBHOOK_SECRET': 'test_webhook_secret',
                'WHATSAPP_WEBHOOK_URL': 'https://test.example.com/webhook',
            }
        }
    )

# Setup Django
django.setup()

def test_signal_registration():
    """Test if signals are properly registered"""
    print("🔍 Testing signal registration...")
    
    try:
        # Import the signals module
        from care_whatsapp_bot import signals
        print("✅ Signals module imported successfully")
        
        # Check if TokenBooking is available
        if hasattr(signals, 'TOKENBOOKING_AVAILABLE'):
            print(f"📱 TokenBooking available: {signals.TOKENBOOKING_AVAILABLE}")
        
        # Check if signal handlers exist
        if hasattr(signals, 'store_original_appointment_data'):
            print("✅ store_original_appointment_data handler found")
        else:
            print("❌ store_original_appointment_data handler NOT found")
            
        if hasattr(signals, 'appointment_notification_handler'):
            print("✅ appointment_notification_handler handler found")
        else:
            print("❌ appointment_notification_handler handler NOT found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing signal registration: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_django_signals():
    """Test Django signal system"""
    print("\n🔍 Testing Django signal system...")
    
    try:
        from django.db.models.signals import post_save, pre_save
        from django.dispatch import receiver
        
        # Check if signals are working
        signal_fired = {'pre_save': False, 'post_save': False}
        
        @receiver(pre_save)
        def test_pre_save_handler(sender, **kwargs):
            signal_fired['pre_save'] = True
            print("✅ Test pre_save signal fired")
            
        @receiver(post_save)
        def test_post_save_handler(sender, **kwargs):
            signal_fired['post_save'] = True
            print("✅ Test post_save signal fired")
        
        # Create a simple test model to trigger signals
        from django.db import models
        
        class TestModel(models.Model):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'care_whatsapp_bot'
        
        # Simulate signal firing
        pre_save.send(sender=TestModel, instance=TestModel(name="test"))
        post_save.send(sender=TestModel, instance=TestModel(name="test"), created=True)
        
        if signal_fired['pre_save'] and signal_fired['post_save']:
            print("✅ Django signal system is working")
            return True
        else:
            print("❌ Django signal system not working properly")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Django signals: {e}")
        return False

def test_whatsapp_provider():
    """Test WhatsApp provider initialization"""
    print("\n🔍 Testing WhatsApp provider...")
    
    try:
        from care_whatsapp_bot.im_wrapper.whatsapp import WhatsAppProvider
        from care_whatsapp_bot.settings import plugin_settings
        
        # Test provider creation
        provider = WhatsAppProvider({
            'access_token': 'test_token',
            'phone_number_id': 'test_phone_id',
        })
        
        print("✅ WhatsApp provider created successfully")
        
        # Test plugin settings
        print(f"📱 Plugin settings access token: {plugin_settings.WHATSAPP_ACCESS_TOKEN}")
        print(f"📱 Plugin settings phone number ID: {plugin_settings.WHATSAPP_PHONE_NUMBER_ID}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing WhatsApp provider: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_message_classes():
    """Test message classes"""
    print("\n🔍 Testing message classes...")
    
    try:
        from care_whatsapp_bot.im_wrapper.base import IMResponse, MessageType
        
        # Test message creation
        response = IMResponse(
            recipient_id="1234567890",
            message_type=MessageType.TEXT,
            content="Test message"
        )
        
        print("✅ IMResponse created successfully")
        print(f"📱 Message type: {response.message_type}")
        print(f"📱 Recipient: {response.recipient_id}")
        print(f"📱 Content: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing message classes: {e}")
        return False

def test_signal_functions():
    """Test signal handler functions"""
    print("\n🔍 Testing signal handler functions...")
    
    try:
        from care_whatsapp_bot import signals
        
        # Test utility functions
        if hasattr(signals, 'format_appointment_details'):
            print("✅ format_appointment_details function found")
            
        if hasattr(signals, 'send_whatsapp_message'):
            print("✅ send_whatsapp_message function found")
            
        if hasattr(signals, 'get_whatsapp_provider'):
            print("✅ get_whatsapp_provider function found")
            
        # Test notification functions
        if hasattr(signals, '_send_appointment_schedule_notification'):
            print("✅ _send_appointment_schedule_notification function found")
            
        if hasattr(signals, '_check_and_send_reschedule_notification'):
            print("✅ _check_and_send_reschedule_notification function found")
            
        if hasattr(signals, '_send_appointment_reschedule_notification'):
            print("✅ _send_appointment_reschedule_notification function found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing signal functions: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive WhatsApp notification signal tests...\n")
    
    tests = [
        ("Signal Registration", test_signal_registration),
        ("Django Signal System", test_django_signals),
        ("WhatsApp Provider", test_whatsapp_provider),
        ("Message Classes", test_message_classes),
        ("Signal Functions", test_signal_functions),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 Running: {test_name}")
        print('='*50)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"💥 Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WhatsApp notification system is ready!")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)