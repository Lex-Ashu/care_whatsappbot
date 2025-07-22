from celery import current_app
from celery.schedules import crontab

from care_whatsapp_bot.tasks import schedule_appointment_reminders


@current_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Set up periodic tasks for the WhatsApp bot
    """
    # Schedule appointment reminders to run daily at 8:00 AM
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        schedule_appointment_reminders.s(days_ahead=7),
        name="schedule_appointment_reminders",
    )