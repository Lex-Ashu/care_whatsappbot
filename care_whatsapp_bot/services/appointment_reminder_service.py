import logging
from datetime import datetime, timedelta

from django.utils import timezone
from django.db.models import Q

from care.facility.models.patient_consultation import PatientConsultation
from care_whatsapp_bot.models import WhatsAppNotification
from care_whatsapp_bot.tasks import send_whatsapp_notification

logger = logging.getLogger(__name__)


class AppointmentReminderService:
    """
    Service to send WhatsApp reminders for upcoming appointments/consultations
    """
    
    def __init__(self):
        self.reminder_days = [1]  # Send reminder 1 day before appointment
        self.reminder_hours = [2]  # Send reminder 2 hours before appointment
    
    def schedule_reminders_for_consultation(self, consultation):
        """
        Schedule reminders for a specific consultation
        
        Args:
            consultation: PatientConsultation object
        """
        try:
            # Check if patient has a phone number
            if not consultation.patient.phone_number:
                logger.info(f"Patient {consultation.patient.id} has no phone number, skipping reminder")
                return
            
            # Format phone number (ensure it has country code)
            phone_number = self._format_phone_number(consultation.patient.phone_number)
            
            # Get appointment date
            appointment_date = consultation.encounter_date
            
            # Schedule day-before reminder
            for days in self.reminder_days:
                reminder_date = appointment_date - timedelta(days=days)
                # Only schedule if reminder date is in the future
                if reminder_date > timezone.now():
                    self._create_reminder_notification(
                        consultation=consultation,
                        phone_number=phone_number,
                        scheduled_at=reminder_date,
                        reminder_type="day"
                    )
            
            # Schedule hours-before reminder
            for hours in self.reminder_hours:
                reminder_date = appointment_date - timedelta(hours=hours)
                # Only schedule if reminder date is in the future
                if reminder_date > timezone.now():
                    self._create_reminder_notification(
                        consultation=consultation,
                        phone_number=phone_number,
                        scheduled_at=reminder_date,
                        reminder_type="hour"
                    )
                    
            logger.info(f"Scheduled reminders for consultation {consultation.id}")
            
        except Exception as e:
            logger.error(f"Error scheduling reminders for consultation {consultation.id}: {e}")
    
    def _create_reminder_notification(self, consultation, phone_number, scheduled_at, reminder_type):
        """
        Create a WhatsApp notification for appointment reminder
        
        Args:
            consultation: PatientConsultation object
            phone_number: Patient's phone number
            scheduled_at: When to send the reminder
            reminder_type: 'day' or 'hour'
        """
        try:
            # Format the appointment details
            facility_name = consultation.facility.name if consultation.facility else "Unknown Facility"
            
            # Get doctor name if available
            doctor_name = "your doctor"
            if consultation.treating_physician:
                doctor_name = f"Dr. {consultation.treating_physician.first_name or ''} {consultation.treating_physician.last_name or ''}".strip()
            
            # Format date and time
            appointment_date = consultation.encounter_date.strftime("%A, %d %B %Y")
            appointment_time = consultation.encounter_date.strftime("%I:%M %p")
            
            # Create appropriate message based on reminder type
            if reminder_type == "day":
                title = "Appointment Reminder"
                message = (
                    f"Hello {consultation.patient.name},\n\n"
                    f"This is a reminder that you have an appointment tomorrow with {doctor_name} at {facility_name}.\n\n"
                    f"📅 Date: {appointment_date}\n"
                    f"⏰ Time: {appointment_time}\n\n"
                    f"Please arrive 15 minutes early. If you need to reschedule, please contact us as soon as possible.\n\n"
                    f"Thank you,\n{facility_name} Team"
                )
            else:  # hour reminder
                title = "Upcoming Appointment Alert"
                message = (
                    f"Hello {consultation.patient.name},\n\n"
                    f"Your appointment with {doctor_name} at {facility_name} is in {self.reminder_hours[0]} hours.\n\n"
                    f"📅 Date: {appointment_date}\n"
                    f"⏰ Time: {appointment_time}\n\n"
                    f"We look forward to seeing you soon.\n\n"
                    f"Thank you,\n{facility_name} Team"
                )
            
            # Create the notification
            notification = WhatsAppNotification.objects.create(
                phone_number=phone_number,
                notification_type='appointment_reminder',
                title=title,
                message=message,
                status='pending',
                patient=consultation.patient,
                scheduled_at=scheduled_at,
                metadata={
                    'consultation_id': str(consultation.external_id),
                    'reminder_type': reminder_type,
                    'facility_id': str(consultation.facility.external_id) if consultation.facility else None,
                }
            )
            
            logger.info(f"Created {reminder_type} reminder notification {notification.id} for consultation {consultation.id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creating reminder notification: {e}")
            return None
    
    def schedule_reminders_for_upcoming_consultations(self, days_ahead=7):
        """
        Schedule reminders for all upcoming consultations in the next X days
        
        Args:
            days_ahead: Number of days to look ahead for consultations
        """
        try:
            # Get current date and end date
            now = timezone.now()
            end_date = now + timedelta(days=days_ahead)
            
            # Find consultations in the date range that don't have discharge dates
            upcoming_consultations = PatientConsultation.objects.filter(
                encounter_date__gte=now,
                encounter_date__lte=end_date,
                discharge_date__isnull=True
            ).select_related('patient', 'facility', 'treating_physician')
            
            logger.info(f"Found {upcoming_consultations.count()} upcoming consultations")
            
            # Schedule reminders for each consultation
            scheduled_count = 0
            for consultation in upcoming_consultations:
                # Skip if patient has no phone number
                if not consultation.patient.phone_number:
                    continue
                    
                # Check if reminders already exist for this consultation
                existing_reminders = WhatsAppNotification.objects.filter(
                    patient=consultation.patient,
                    notification_type='appointment_reminder',
                    status='pending',
                    metadata__consultation_id=str(consultation.external_id)
                ).exists()
                
                # If no reminders exist, schedule them
                if not existing_reminders:
                    self.schedule_reminders_for_consultation(consultation)
                    scheduled_count += 1
            
            logger.info(f"Scheduled reminders for {scheduled_count} consultations")
            return {
                'status': 'success',
                'total_consultations': upcoming_consultations.count(),
                'scheduled_reminders': scheduled_count
            }
            
        except Exception as e:
            logger.error(f"Error scheduling reminders for upcoming consultations: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _format_phone_number(self, phone_number):
        """
        Ensure phone number has country code
        
        Args:
            phone_number: Phone number string
        
        Returns:
            Formatted phone number with country code
        """
        # Remove any non-digit characters
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        # Add India country code (91) if not present
        if not phone_number.startswith('91') and len(phone_number) == 10:
            phone_number = '91' + phone_number
            
        return phone_number