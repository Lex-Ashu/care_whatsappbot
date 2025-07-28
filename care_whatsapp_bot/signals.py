import logging
import sys
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from care_whatsapp_bot.services.whatsapp_notification_service import WhatsAppNotificationService
from care_whatsapp_bot.settings import plugin_settings
from django.utils import timezone

try:
    from care.emr.models.scheduling.booking import TokenBooking
    TOKENBOOKING_AVAILABLE = True
except ImportError:
    TOKENBOOKING_AVAILABLE = False
    class TokenBooking:
        pass

logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

_appointment_cache = {}
notification_service = WhatsAppNotificationService()

if TOKENBOOKING_AVAILABLE:
    @receiver(pre_save, sender=TokenBooking)
    def store_original_appointment_data(sender, instance, **kwargs):
        if instance.pk:
            try:
                original = TokenBooking.objects.get(pk=instance.pk)
                _appointment_cache[instance.pk] = {
                    'original_slot_id': original.token_slot.id if original.token_slot else None,
                    'original_start_time': original.token_slot.start_datetime if original.token_slot else None,
                }
            except TokenBooking.DoesNotExist:
                pass
            except Exception as e:
                logger.error(f"Error storing original appointment data: {str(e)}")

    @receiver(post_save, sender=TokenBooking)
    def appointment_notification_handler(sender, instance, created, **kwargs):
        try:
            if created:
                notification_service.send_appointment_schedule_notification(instance)
            else:
                _check_and_send_reschedule_notification(instance)
        except Exception as e:
            logger.error(f"Error in appointment notification handler: {str(e)}")
        finally:
            if instance.pk in _appointment_cache:
                del _appointment_cache[instance.pk]

def _check_and_send_reschedule_notification(instance):
    if instance.pk not in _appointment_cache:
        return
    
    try:
        original_data = _appointment_cache[instance.pk]
        current_slot = getattr(instance, 'token_slot', None)
        
        if not current_slot:
            return
            
        current_slot_id = current_slot.id
        original_slot_id = original_data.get('original_slot_id')
        
        if original_slot_id and current_slot_id != original_slot_id:
            notification_service.send_appointment_reschedule_notification(instance, original_data)
            
    except Exception as e:
        logger.error(f"Error checking for reschedule: {str(e)}")

try:
    from care.patient.models import Patient
    PATIENT_AVAILABLE = True
except ImportError:
    PATIENT_AVAILABLE = False

if PATIENT_AVAILABLE:
    @receiver(post_save, sender=Patient)
    def discharge_summary_notification_handler(sender, instance, created, **kwargs):
        if not created:
            try:
                if hasattr(instance, 'status') and instance.status == 'discharged':
                    discharge_data = {
                        'discharge_date': timezone.now().strftime('%A, %B %d, %Y'),
                        'hospital_name': 'CARE Hospital',
                        'doctor_name': 'Doctor',
                        'summary': 'Your discharge summary is ready. Please contact the hospital for detailed information.',
                    }
                    
                    notification_service.send_discharge_summary_notification(instance, discharge_data)
                    
            except Exception as e:
                logger.error(f"Error in discharge summary notification handler: {str(e)}")