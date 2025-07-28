import logging
from care_whatsapp_bot.services.whatsapp_notification_service import WhatsAppNotificationService
from care_whatsapp_bot.im_wrapper.whatsapp import WhatsAppProvider
from care_whatsapp_bot.im_wrapper.base import IMResponse, MessageType
from care_whatsapp_bot.settings import plugin_settings

logger = logging.getLogger(__name__)

class MessageRouter:
    def __init__(self):
        self.whatsapp = WhatsAppProvider({
            'access_token': plugin_settings.WHATSAPP_ACCESS_TOKEN,
            'phone_number_id': plugin_settings.WHATSAPP_PHONE_NUMBER_ID,
        })
        self.notification_service = WhatsAppNotificationService()

    def route(self, sender, text):
        text = text.strip().lower()
        
        try:
            patient = self._get_patient_by_phone(sender)
            
            if text in ["view appointments", "appointments", "1"]:
                return self._handle_view_appointments(sender, patient)
            elif text in ["about care", "about", "2"]:
                return self._handle_about_care(sender)
            elif text in ["help", "menu", "start"]:
                return self._handle_menu(sender)
            else:
                return self._handle_welcome(sender, patient)
                
        except Exception as e:
            logger.error(f"Error routing message: {str(e)}")
            return self._handle_error(sender)

    def _get_patient_by_phone(self, phone_number):
        try:
            from care.patient.models import Patient
            return Patient.objects.filter(phone_number=phone_number).first()
        except Exception as e:
            logger.error(f"Error getting patient by phone: {str(e)}")
            return None

    def _handle_menu(self, sender):
        msg = """Welcome to CARE!

I'm your healthcare assistant. Here's what I can help you with:

1. View Appointments - Check your upcoming appointments
2. About Care - Learn more about CARE

Reply with the number or text to get started!"""
        
        response = IMResponse(
            recipient_id=sender,
            message_type=MessageType.TEXT,
            content=msg
        )
        self.whatsapp.send_message(response)

    def _handle_welcome(self, sender, patient):
        if patient:
            self.notification_service.send_welcome_message(sender, getattr(patient, 'name', None))
        else:
            msg = """Welcome to CARE!

I'm your healthcare assistant. To get started, please:

1. View Appointments - Check your appointments
2. About Care - Learn more about us

Reply with your choice!"""
            
            response = IMResponse(
                recipient_id=sender,
                message_type=MessageType.TEXT,
                content=msg
            )
            self.whatsapp.send_message(response)

    def _handle_view_appointments(self, sender, patient):
        if not patient:
            msg = "Sorry, I couldn't find your patient record. Please contact the hospital to link your phone number."
            response = IMResponse(
                recipient_id=sender,
                message_type=MessageType.TEXT,
                content=msg
            )
            self.whatsapp.send_message(response)
            return
        
        try:
            appointments_data = self.notification_service.get_patient_appointments(patient)
            
            if appointments_data:
                self.notification_service.send_appointments_list(sender, appointments_data)
            else:
                msg = "You have no upcoming appointments scheduled."
                response = IMResponse(
                    recipient_id=sender,
                    message_type=MessageType.TEXT,
                    content=msg
                )
                self.whatsapp.send_message(response)
                
        except Exception as e:
            logger.error(f"Error handling view appointments: {str(e)}")
            msg = "Sorry, I couldn't retrieve your appointments. Please try again later."
            response = IMResponse(
                recipient_id=sender,
                message_type=MessageType.TEXT,
                content=msg
            )
            self.whatsapp.send_message(response)

    def _handle_about_care(self, sender):
        self.notification_service.send_about_care_message(sender)

    def _handle_error(self, sender):
        msg = "Sorry, something went wrong. Please try again or contact support."
        response = IMResponse(
            recipient_id=sender,
            message_type=MessageType.TEXT,
            content=msg
        )
        self.whatsapp.send_message(response)