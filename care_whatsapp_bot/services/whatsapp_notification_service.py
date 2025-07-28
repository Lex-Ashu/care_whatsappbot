import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.template import Template, Context
from care_whatsapp_bot.models.whatsapp import WhatsAppMessage, WhatsAppTemplate
from care_whatsapp_bot.im_wrapper.whatsapp import WhatsAppProvider
from care_whatsapp_bot.im_wrapper.base import IMResponse, MessageType
from care_whatsapp_bot.settings import plugin_settings

logger = logging.getLogger(__name__)

class WhatsAppNotificationService:
    def __init__(self):
        self.whatsapp_provider = WhatsAppProvider({
            'access_token': plugin_settings.WHATSAPP_ACCESS_TOKEN,
            'phone_number_id': plugin_settings.WHATSAPP_PHONE_NUMBER_ID,
        })
    
    def send_appointment_schedule_notification(self, appointment):
        """Send appointment schedule notification to patient and practitioner"""
        logger.info(f"Sending appointment schedule notification for booking {appointment.pk}")
        
        try:
            patient = getattr(appointment, 'patient', None)
            slot = getattr(appointment, 'token_slot', None)
            practitioner = None
            
            if slot and hasattr(slot, 'resource') and slot.resource:
                practitioner = getattr(slot.resource, 'user', None)
            
            # Send to patient
            if patient and hasattr(patient, 'phone_number') and patient.phone_number:
                self._send_template_message(
                    'appointment_schedule_patient',
                    patient.phone_number,
                    {
                        'patient_name': getattr(patient, 'name', 'Patient'),
                        'appointment_date': slot.start_datetime.strftime('%A, %B %d, %Y') if slot else 'Unknown',
                        'appointment_time': slot.start_datetime.strftime('%I:%M %p') if slot else 'Unknown',
                        'location': getattr(slot.resource, 'name', 'Unknown Location') if slot and slot.resource else 'Unknown',
                        'practitioner_name': getattr(practitioner, 'first_name', 'Doctor') if practitioner else 'Doctor',
                    }
                )
            
            # Send to practitioner
            if practitioner and hasattr(practitioner, 'phone_number') and practitioner.phone_number:
                self._send_template_message(
                    'appointment_schedule_practitioner',
                    practitioner.phone_number,
                    {
                        'practitioner_name': getattr(practitioner, 'first_name', 'Doctor'),
                        'patient_name': getattr(patient, 'name', 'Unknown') if patient else 'Unknown',
                        'appointment_date': slot.start_datetime.strftime('%A, %B %d, %Y') if slot else 'Unknown',
                        'appointment_time': slot.start_datetime.strftime('%I:%M %p') if slot else 'Unknown',
                        'location': getattr(slot.resource, 'name', 'Unknown Location') if slot and slot.resource else 'Unknown',
                    }
                )
                
        except Exception as e:
            logger.error(f"Error sending appointment schedule notification: {str(e)}")
    
    def send_appointment_reschedule_notification(self, appointment, original_data):
        """Send appointment reschedule notification to patient and practitioner"""
        logger.info(f"Sending appointment reschedule notification for booking {appointment.pk}")
        
        try:
            patient = getattr(appointment, 'patient', None)
            slot = getattr(appointment, 'token_slot', None)
            practitioner = None
            
            if slot and hasattr(slot, 'resource') and slot.resource:
                practitioner = getattr(slot.resource, 'user', None)
            
            original_time = original_data.get('original_start_time')
            original_date = original_time.strftime('%A, %B %d, %Y') if original_time else 'Unknown'
            original_time_str = original_time.strftime('%I:%M %p') if original_time else 'Unknown'
            
            # Send to patient
            if patient and hasattr(patient, 'phone_number') and patient.phone_number:
                self._send_template_message(
                    'appointment_reschedule_patient',
                    patient.phone_number,
                    {
                        'patient_name': getattr(patient, 'name', 'Patient'),
                        'original_date': original_date,
                        'original_time': original_time_str,
                        'new_date': slot.start_datetime.strftime('%A, %B %d, %Y') if slot else 'Unknown',
                        'new_time': slot.start_datetime.strftime('%I:%M %p') if slot else 'Unknown',
                        'location': getattr(slot.resource, 'name', 'Unknown Location') if slot and slot.resource else 'Unknown',
                    }
                )
            
            # Send to practitioner
            if practitioner and hasattr(practitioner, 'phone_number') and practitioner.phone_number:
                self._send_template_message(
                    'appointment_reschedule_practitioner',
                    practitioner.phone_number,
                    {
                        'practitioner_name': getattr(practitioner, 'first_name', 'Doctor'),
                        'patient_name': getattr(patient, 'name', 'Unknown') if patient else 'Unknown',
                        'original_date': original_date,
                        'original_time': original_time_str,
                        'new_date': slot.start_datetime.strftime('%A, %B %d, %Y') if slot else 'Unknown',
                        'new_time': slot.start_datetime.strftime('%I:%M %p') if slot else 'Unknown',
                        'location': getattr(slot.resource, 'name', 'Unknown Location') if slot and slot.resource else 'Unknown',
                    }
                )
                
        except Exception as e:
            logger.error(f"Error sending appointment reschedule notification: {str(e)}")
    
    def send_discharge_summary_notification(self, patient, discharge_data):
        """Send discharge summary notification to patient"""
        logger.info(f"Sending discharge summary notification for patient {patient.pk}")
        
        try:
            if patient and hasattr(patient, 'phone_number') and patient.phone_number:
                self._send_template_message(
                    'discharge_summary_patient',
                    patient.phone_number,
                    {
                        'patient_name': getattr(patient, 'name', 'Patient'),
                        'discharge_date': discharge_data.get('discharge_date', 'Unknown'),
                        'hospital_name': discharge_data.get('hospital_name', 'CARE Hospital'),
                        'doctor_name': discharge_data.get('doctor_name', 'Doctor'),
                        'summary': discharge_data.get('summary', 'Discharge summary available'),
                    }
                )
        except Exception as e:
            logger.error(f"Error sending discharge summary notification: {str(e)}")
    
    def send_welcome_message(self, phone_number, patient_name=None):
        """Send welcome message to new user"""
        logger.info(f"Sending welcome message to {phone_number}")
        
        try:
            self._send_template_message(
                'welcome_message',
                phone_number,
                {
                    'patient_name': patient_name or 'there',
                }
            )
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}")
    
    def send_appointments_list(self, phone_number, appointments_data):
        """Send appointments list to user"""
        logger.info(f"Sending appointments list to {phone_number}")
        
        try:
            self._send_template_message(
                'appointments_list',
                phone_number,
                {
                    'appointments_count': len(appointments_data),
                    'appointments_list': appointments_data,
                }
            )
        except Exception as e:
            logger.error(f"Error sending appointments list: {str(e)}")
    
    def send_about_care_message(self, phone_number):
        """Send about CARE message"""
        logger.info(f"Sending about CARE message to {phone_number}")
        
        try:
            self._send_template_message(
                'about_care',
                phone_number,
                {}
            )
        except Exception as e:
            logger.error(f"Error sending about CARE message: {str(e)}")
    
    def _send_template_message(self, template_type, phone_number, variables):
        """Send message using template with variables"""
        try:
            template = WhatsAppTemplate.objects.filter(
                template_type=template_type,
                is_enabled=True
            ).first()
            
            if not template:
                logger.warning(f"Template {template_type} not found or disabled")
                return False
            
            # Render template with variables
            template_obj = Template(template.content)
            context = Context(variables)
            rendered_content = template_obj.render(context)
            
            # Create message record
            message = WhatsAppMessage.objects.create(
                recipient_phone=phone_number,
                message_type=template_type,
                content=rendered_content,
                status='pending'
            )
            
            # Send via WhatsApp
            response = IMResponse(
                recipient_id=phone_number,
                message_type=MessageType.TEXT,
                content=rendered_content
            )
            
            success = self.whatsapp_provider.send_message(response)
            
            if success:
                message.status = 'sent'
                message.sent_at = timezone.now()
                message.save()
                logger.info(f"Message sent successfully to {phone_number}")
                return True
            else:
                message.status = 'failed'
                message.error_message = 'Failed to send via WhatsApp API'
                message.save()
                logger.error(f"Failed to send message to {phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"Error in _send_template_message: {str(e)}")
            return False
    
    def update_message_status(self, whatsapp_message_id, status, timestamp=None):
        """Update message status based on WhatsApp webhook"""
        try:
            message = WhatsAppMessage.objects.filter(
                whatsapp_message_id=whatsapp_message_id
            ).first()
            
            if message:
                if status == 'delivered':
                    message.status = 'delivered'
                    message.delivered_at = timestamp or timezone.now()
                elif status == 'read':
                    message.status = 'read'
                    message.read_at = timestamp or timezone.now()
                
                message.save()
                logger.info(f"Updated message {whatsapp_message_id} status to {status}")
                
        except Exception as e:
            logger.error(f"Error updating message status: {str(e)}")
    
    def get_patient_appointments(self, patient):
        """Get upcoming appointments for a patient"""
        try:
            from care.emr.models.scheduling.booking import TokenBooking
            
            upcoming_appointments = TokenBooking.objects.filter(
                patient=patient,
                token_slot__start_datetime__gte=timezone.now(),
                deleted=False
            ).select_related('token_slot', 'token_slot__resource').order_by('token_slot__start_datetime')[:10]
            
            appointments_data = []
            for appointment in upcoming_appointments:
                slot = appointment.token_slot
                appointments_data.append({
                    'date': slot.start_datetime.strftime('%A, %B %d, %Y'),
                    'time': slot.start_datetime.strftime('%I:%M %p'),
                    'location': getattr(slot.resource, 'name', 'Unknown Location') if slot.resource else 'Unknown',
                    'practitioner': getattr(slot.resource.user, 'first_name', 'Doctor') if slot.resource and slot.resource.user else 'Doctor',
                })
            
            return appointments_data
            
        except Exception as e:
            logger.error(f"Error getting patient appointments: {str(e)}")
            return [] 