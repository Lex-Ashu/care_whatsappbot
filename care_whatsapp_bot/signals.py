from django.db.models.signals import post_save
from django.dispatch import receiver
from care_whatsapp_bot.im_wrapper.whatsapp import WhatsAppProvider
from care_whatsapp_bot.settings import plugin_settings

# Import your TokenBooking model from CARE
from care.emr.models.scheduling.booking import TokenBooking

print("[PLUGIN] TokenBooking id:", id(TokenBooking), "module:", TokenBooking.__module__)

# Try to import IMResponse and MessageType, fallback to simple text if not available
try:
    from care_whatsapp_bot.im_wrapper.base import IMResponse, MessageType
except ImportError:
    IMResponse = None
    MessageType = None

@receiver(post_save, sender=TokenBooking)
def appointment_schedule_notification(sender, instance, created, **kwargs):
    print("[SIGNAL] TokenBooking id:", id(TokenBooking), "module:", TokenBooking.__module__)
    print("TokenBooking post_save signal fired", instance)
    if created:
        whatsapp = WhatsAppProvider({
            'access_token': plugin_settings.WHATSAPP_ACCESS_TOKEN,
            'phone_number_id': plugin_settings.WHATSAPP_PHONE_NUMBER_ID,
        })
        patient = getattr(instance, 'patient', None)
        practitioner = getattr(instance.token_slot.resource, 'user', None)
        slot = getattr(instance, 'token_slot', None)
        # Compose appointment details
        details = f"Appointment scheduled on {slot.start_datetime.strftime('%Y-%m-%d %H:%M')}"
        # Send to patient
        if patient and hasattr(patient, 'phone_number'):
            if IMResponse and MessageType:
                whatsapp.send_message(IMResponse(
                    recipient_id=patient.phone_number,
                    message_type=MessageType.TEXT,
                    content=f"Your appointment is scheduled. {details}"
                ))
            else:
                whatsapp.send_message(patient.phone_number, f"Your appointment is scheduled. {details}")
        # Send to practitioner
        if practitioner and hasattr(practitioner, 'phone_number'):
            if IMResponse and MessageType:
                whatsapp.send_message(IMResponse(
                    recipient_id=practitioner.phone_number,
                    message_type=MessageType.TEXT,
                    content=f"You have a new appointment scheduled. {details}"
                ))
            else:
                whatsapp.send_message(practitioner.phone_number, f"You have a new appointment scheduled. {details}")