# WhatsApp Notification Services

## Appointment Reminder Service

The Appointment Reminder Service is responsible for sending WhatsApp notifications to patients about their upcoming appointments. It helps reduce no-shows and improves patient engagement.

### Features

- Automatically schedules reminders for upcoming appointments
- Sends reminders 1 day before and 2 hours before appointments
- Customized messages with appointment details (date, time, doctor, facility)
- Prevents duplicate reminders for the same appointment

### How It Works

1. The service scans for upcoming consultations in the next 7 days
2. For each consultation, it creates two WhatsApp notifications:
   - A day-before reminder
   - A few-hours-before reminder
3. Notifications are scheduled to be sent at the appropriate times
4. The Celery beat scheduler runs this service daily at 8:00 AM

### Usage

#### Automatic Scheduling

The service runs automatically via Celery beat scheduler. No manual intervention is required.

#### Manual Scheduling

You can manually trigger the service using the management command:

```bash
# Schedule reminders for appointments in the next 7 days
python manage.py schedule_appointment_reminders

# Schedule reminders for appointments in the next X days
python manage.py schedule_appointment_reminders --days=10

# Run asynchronously using Celery
python manage.py schedule_appointment_reminders --async
```

#### Programmatic Usage

```python
from care_whatsapp_bot.services.appointment_reminder_service import AppointmentReminderService

# Schedule reminders for all upcoming consultations
service = AppointmentReminderService()
result = service.schedule_reminders_for_upcoming_consultations(days_ahead=7)

# Schedule reminders for a specific consultation
from care.facility.models.patient_consultation import PatientConsultation
consultation = PatientConsultation.objects.get(id=consultation_id)
service.schedule_reminders_for_consultation(consultation)
```