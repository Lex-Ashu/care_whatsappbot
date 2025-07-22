from django.db.models.signals import post_save
from django.dispatch import receiver
from care_whatsapp_bot.im_wrapper.whatsapp import WhatsAppProvider
from care_whatsapp_bot.settings import plugin_settings

# Import your TokenBooking model from CARE
from care.emr.models.scheduling.booking import TokenBooking

@receiver(post_save, sender=TokenBooking)
def appointment_schedule_notification(sender, instance, created, **kwargs):
    if created:
        whatsapp = WhatsAppProvider({
            'access_token': plugin_settings.WHATSAPP_ACCESS_TOKEN,
            'phone_number_id': plugin_settings.WHATSAPP_PHONE_NUMBER_ID,
        })
        patient = getattr(instance, 'patient', None)
        practitioner = getattr(instance.token_slot.resource, 'user', None)
        if patient and hasattr(patient, 'phone_number'):
            whatsapp.send_message(patient.phone_number, f"Your appointment is scheduled.")
        if practitioner and hasattr(practitioner, 'phone_number'):
            whatsapp.send_message(practitioner.phone_number, f"You have a new appointment scheduled.") 