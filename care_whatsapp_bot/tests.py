from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from unittest.mock import patch, MagicMock
import json
from datetime import timedelta

from .models.whatsapp import (
    WhatsAppSession,
    WhatsAppMessage,
    WhatsAppCommand,
    WhatsAppNotification
)
from .authentication import WhatsAppAuthenticator
from .message_router import MessageRouter
from .im_wrapper.whatsapp import WhatsAppProvider
from .im_wrapper.base import IMMessage, MessageType, IMResponse


class WhatsAppModelTests(TestCase):
    """Test WhatsApp models"""
    
    def setUp(self):
        self.phone_number = "+1234567890"
        self.user_id = "test_user_123"
    
    def test_whatsapp_session_creation(self):
        """Test WhatsApp session creation"""
        session = WhatsAppSession.objects.create(
            phone_number=self.phone_number,
            user_type='patient',
            user_id=self.user_id
        )
        
        self.assertEqual(session.phone_number, self.phone_number)
        self.assertEqual(session.user_type, 'patient')
        self.assertEqual(session.user_id, self.user_id)
        self.assertFalse(session.is_authenticated)
        self.assertTrue(session.is_active)
    
    def test_session_authentication(self):
        """Test session authentication"""
        session = WhatsAppSession.objects.create(
            phone_number=self.phone_number,
            user_type='patient',
            user_id=self.user_id,
            is_authenticated=True
        )
        
        self.assertTrue(session.is_authenticated)
        self.assertTrue(session.is_active)
    
    def test_whatsapp_message_creation(self):
        """Test WhatsApp message creation"""
        session = WhatsAppSession.objects.create(
            phone_number=self.phone_number,
            user_type='patient'
        )
        
        message = WhatsAppMessage.objects.create(
            session=session,
            direction='incoming',
            message_type='text',
            content='Hello',
            whatsapp_message_id='msg_123'
        )
        
        self.assertEqual(message.session, session)
        self.assertEqual(message.direction, 'incoming')
        self.assertEqual(message.content, 'Hello')
        self.assertFalse(message.is_processed)
        
        # Test mark processed
        message.mark_processed()
        self.assertTrue(message.is_processed)
        self.assertIsNotNone(message.processed_at)
    
    def test_whatsapp_command_creation(self):
        """Test WhatsApp command creation"""
        session = WhatsAppSession.objects.create(
            phone_number=self.phone_number,
            user_type='patient'
        )
        
        command = WhatsAppCommand.objects.create(
            session=session,
            command_type='help',
            command_data={'action': 'show_help'},
            is_successful=True
        )
        
        self.assertEqual(command.session, session)
        self.assertEqual(command.command_type, 'help')
        self.assertTrue(command.is_successful)
        self.assertIsNotNone(command.executed_at)
    
    def test_whatsapp_notification_creation(self):
        """Test WhatsApp notification creation"""
        notification = WhatsAppNotification.objects.create(
            patient_id=self.user_id,
            notification_type='appointment_reminder',
            content='You have an appointment tomorrow',
            scheduled_at=timezone.now()
        )
        
        self.assertEqual(notification.patient_id, self.user_id)
        self.assertEqual(notification.status, 'pending')
        
        # Test mark sent
        notification.mark_sent('msg_123')
        self.assertEqual(notification.status, 'sent')
        self.assertEqual(notification.whatsapp_message_id, 'msg_123')
        self.assertIsNotNone(notification.sent_at)


class WhatsAppAuthenticatorTests(TestCase):
    """Test WhatsApp authenticator"""
    
    def setUp(self):
        self.authenticator = WhatsAppAuthenticator()
        self.phone_number = "+1234567890"
        self.user_id = "test_user_123"
    
    def test_phone_number_normalization(self):
        """Test phone number normalization"""
        test_cases = [
            ("1234567890", "+1234567890"),
            ("+1234567890", "+1234567890"),
            ("91-9876543210", "+919876543210"),
            (" +1 234 567 890 ", "+1234567890")
        ]
        
        for input_phone, expected in test_cases:
            normalized = self.authenticator._normalize_phone_number(input_phone)
            self.assertEqual(normalized, expected)
    
    def test_user_type_identification(self):
        """Test user type identification"""
        # Test unknown user (default case)
        user_type = self.authenticator.identify_user_type(self.phone_number)
        self.assertEqual(user_type, 'unknown')
    
    @patch('care_whatsapp_bot.utils.sms_utils.send_sms')
    def test_otp_generation_and_verification(self, mock_send_sms):
        """Test OTP generation and verification"""
        mock_send_sms.return_value = True
        
        # Generate OTP
        result = self.authenticator.generate_otp(self.phone_number)
        self.assertTrue(result['success'])
        
        # Get OTP from cache for testing
        cache_key = f"whatsapp_otp:{self.phone_number}"
        otp_data = cache.get(cache_key)
        self.assertIsNotNone(otp_data)
        
        otp = otp_data['otp']
        
        # Verify correct OTP
        result = self.authenticator.verify_otp(self.phone_number, otp)
        self.assertTrue(result['success'])
        
        # Verify incorrect OTP
        result = self.authenticator.verify_otp(self.phone_number, '000000')
        self.assertFalse(result['success'])
    
    def test_session_management(self):
        """Test session creation and retrieval"""
        # Create session
        session = self.authenticator.create_session(
            self.phone_number, 'patient', user_id=self.user_id
        )
        
        self.assertEqual(session.phone_number, self.phone_number)
        self.assertEqual(session.user_type, 'patient')
        self.assertEqual(session.user_id, self.user_id)
        self.assertTrue(session.is_authenticated)
        
        # Get session
        retrieved_session = self.authenticator.get_session(self.phone_number)
        self.assertEqual(retrieved_session.id, session.id)
        
        # Logout
        self.authenticator.logout(self.phone_number)
        logged_out_session = self.authenticator.get_session(self.phone_number)
        self.assertFalse(logged_out_session.is_authenticated)


class MessageRouterTests(TestCase):
    """Test message router functionality"""
    
    def setUp(self):
        self.router = MessageRouter()
        self.phone_number = "+1234567890"
        self.session = WhatsAppSession.objects.create(
            phone_number=self.phone_number,
            user_type='patient',
            is_authenticated=True
        )
    
    def test_message_parsing(self):
        """Test message parsing"""
        # Test help command
        parsed = self.router.parse_message("help")
        self.assertEqual(parsed['command'], 'help')
        
        # Test menu command
        parsed = self.router.parse_message("menu")
        self.assertEqual(parsed['command'], 'menu')
        
        # Test regular text
        parsed = self.router.parse_message("Hello there")
        self.assertEqual(parsed['command'], 'unknown')
    
    @patch('care_whatsapp_bot.im_wrapper.whatsapp.WhatsAppProvider.send_message')
    def test_message_routing(self, mock_send):
        """Test message routing"""
        mock_send.return_value = IMResponse(success=True, message_id='msg_123')
        
        # Create incoming message
        message = WhatsAppMessage.objects.create(
            session=self.session,
            direction='incoming',
            message_type='text',
            content='help',
            whatsapp_message_id='incoming_123'
        )
        
        # Route message
        response = self.router.route_message(message)
        
        self.assertIsNotNone(response)
        mock_send.assert_called()


class WhatsAppProviderTests(TestCase):
    """Test WhatsApp provider functionality"""
    
    def setUp(self):
        self.provider = WhatsAppProvider()
        self.phone_number = "+1234567890"
    
    @patch('requests.post')
    def test_send_text_message(self, mock_post):
        """Test sending text message"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'messages': [{'id': 'msg_123'}]
        }
        mock_post.return_value = mock_response
        
        message = IMMessage(
            to=self.phone_number,
            content="Hello World",
            message_type=MessageType.TEXT
        )
        
        response = self.provider.send_message(message)
        
        self.assertTrue(response.success)
        self.assertEqual(response.message_id, 'msg_123')
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_message_failure(self, mock_post):
        """Test message sending failure"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {'message': 'Invalid phone number'}
        }
        mock_post.return_value = mock_response
        
        message = IMMessage(
            to="invalid_phone",
            content="Hello World",
            message_type=MessageType.TEXT
        )
        
        response = self.provider.send_message(message)
        
        self.assertFalse(response.success)
        self.assertIn('Invalid phone number', response.error)


class WhatsAppWebhookTests(TestCase):
    """Test WhatsApp webhook functionality"""
    
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('care_whatsapp_bot:whatsapp-webhook')
        self.phone_number = "+1234567890"
    
    def test_webhook_verification(self):
        """Test webhook verification"""
        with self.settings(WHATSAPP_WEBHOOK_VERIFY_TOKEN='test_token'):
            response = self.client.get(self.webhook_url, {
                'hub.mode': 'subscribe',
                'hub.challenge': 'test_challenge',
                'hub.verify_token': 'test_token'
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), 'test_challenge')
    
    def test_webhook_verification_failure(self):
        """Test webhook verification failure"""
        with self.settings(WHATSAPP_WEBHOOK_VERIFY_TOKEN='test_token'):
            response = self.client.get(self.webhook_url, {
                'hub.mode': 'subscribe',
                'hub.challenge': 'test_challenge',
                'hub.verify_token': 'wrong_token'
            })
            
            self.assertEqual(response.status_code, 403)
    
    @patch('care_whatsapp_bot.tasks.process_whatsapp_message.delay')
    def test_incoming_message_webhook(self, mock_task):
        """Test incoming message webhook"""
        webhook_data = {
            'object': 'whatsapp_business_account',
            'entry': [{
                'id': 'entry_id',
                'changes': [{
                    'value': {
                        'messaging_product': 'whatsapp',
                        'messages': [{
                            'id': 'msg_123',
                            'from': self.phone_number.replace('+', ''),
                            'timestamp': '1234567890',
                            'type': 'text',
                            'text': {'body': 'Hello'}
                        }]
                    },
                    'field': 'messages'
                }]
            }]
        }
        
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        mock_task.assert_called_once()
    
    def test_health_check(self):
        """Test health check endpoint"""
        health_url = reverse('care_whatsapp_bot:whatsapp-health')
        response = self.client.get(health_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)


class TaskTests(TestCase):
    """Test Celery tasks"""
    
    def setUp(self):
        self.phone_number = "+1234567890"
        self.session = WhatsAppSession.objects.create(
            phone_number=self.phone_number,
            user_type='patient'
        )
    
    @patch('care_whatsapp_bot.message_router.MessageRouter.route_message')
    def test_process_whatsapp_message_task(self, mock_router):
        """Test process WhatsApp message task"""
        from .tasks import process_whatsapp_message
        
        mock_router.return_value = "Message processed"
        
        message_data = {
            'id': 'msg_123',
            'from': self.phone_number.replace('+', ''),
            'timestamp': '1234567890',
            'type': 'text',
            'text': {'body': 'Hello'}
        }
        
        # Run task synchronously for testing
        result = process_whatsapp_message(message_data)
        
        self.assertTrue(result)
        mock_router.assert_called_once()
    
    @patch('care_whatsapp_bot.im_wrapper.whatsapp.WhatsAppProvider.send_message')
    def test_send_whatsapp_notification_task(self, mock_send):
        """Test send WhatsApp notification task"""
        from .tasks import send_whatsapp_notification
        
        mock_send.return_value = IMResponse(success=True, message_id='msg_123')
        
        notification = WhatsAppNotification.objects.create(
            patient_id='patient_123',
            notification_type='appointment_reminder',
            content='You have an appointment tomorrow',
            scheduled_at=timezone.now()
        )
        
        # Run task synchronously for testing
        result = send_whatsapp_notification(notification.id)
        
        self.assertTrue(result)
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'sent')
        mock_send.assert_called_once()


def test_cleanup_old_notifications_respects_retention_days(self):
    from care_whatsapp_bot.signals import cleanup_old_notifications
    from care_whatsapp_bot.models.whatsapp import WhatsAppNotification
    from care_whatsapp_bot.settings import plugin_settings
    from django.utils import timezone
    from datetime import timedelta

    # Create a notification older than retention period
    retention_days = plugin_settings.NOTIFICATION_RETENTION_DAYS
    old_date = timezone.now() - timedelta(days=retention_days + 1)
    notification = WhatsAppNotification.objects.create(
        phone_number="+1234567890",
        notification_type="test",
        title="Old Notification",
        message="This is old",
        status="sent",
        created_at=old_date,
        scheduled_at=old_date
    )
    # Create a notification within retention period
    recent_date = timezone.now() - timedelta(days=retention_days - 1)
    notification2 = WhatsAppNotification.objects.create(
        phone_number="+1234567891",
        notification_type="test",
        title="Recent Notification",
        message="This is recent",
        status="sent",
        created_at=recent_date,
        scheduled_at=recent_date
    )
    cleanup_old_notifications()
    # Old notification should be deleted, recent should remain
    self.assertFalse(WhatsAppNotification.objects.filter(id=notification.id).exists())
    self.assertTrue(WhatsAppNotification.objects.filter(id=notification2.id).exists())


def test_delete_old_notifications_task(self):
    from care_whatsapp_bot.signals import delete_old_notifications
    from care_whatsapp_bot.models.whatsapp import WhatsAppNotification
    from django.conf import settings
    from django.utils import timezone
    from datetime import timedelta

    retention_days = getattr(settings, 'NOTIFICATION_RETENTION_DAYS', 30)
    old_date = timezone.now() - timedelta(days=retention_days + 1)
    notification = WhatsAppNotification.objects.create(
        phone_number="+1234567890",
        notification_type="test",
        title="Old Notification",
        message="This is old",
        status="sent",
        created_at=old_date,
        scheduled_at=old_date
    )
    recent_date = timezone.now() - timedelta(days=retention_days - 1)
    notification2 = WhatsAppNotification.objects.create(
        phone_number="+1234567891",
        notification_type="test",
        title="Recent Notification",
        message="This is recent",
        status="sent",
        created_at=recent_date,
        scheduled_at=recent_date
    )
    delete_old_notifications()
    self.assertFalse(WhatsAppNotification.objects.filter(id=notification.id).exists())
    self.assertTrue(WhatsAppNotification.objects.filter(id=notification2.id).exists())