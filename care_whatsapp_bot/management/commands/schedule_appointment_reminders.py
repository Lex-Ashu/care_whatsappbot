import logging
from django.core.management.base import BaseCommand

from care_whatsapp_bot.tasks import schedule_appointment_reminders

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Schedule WhatsApp reminders for upcoming appointments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to look ahead for appointments (default: 7)'
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run asynchronously using Celery (default: False)'
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        run_async = options['async']
        
        self.stdout.write(
            self.style.SUCCESS(f"Scheduling appointment reminders for the next {days_ahead} days")
        )
        
        try:
            if run_async:
                # Run as a Celery task
                task = schedule_appointment_reminders.delay(days_ahead=days_ahead)
                self.stdout.write(
                    self.style.SUCCESS(f"Task scheduled with ID: {task.id}")
                )
            else:
                # Run synchronously
                result = schedule_appointment_reminders(days_ahead=days_ahead)
                
                if result['status'] == 'success':
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully scheduled reminders for {result['scheduled_reminders']} "
                            f"out of {result['total_consultations']} upcoming consultations"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Error: {result['error']}")
                    )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error scheduling appointment reminders: {e}")
            )