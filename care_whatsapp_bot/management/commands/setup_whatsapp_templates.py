from django.core.management.base import BaseCommand
from care_whatsapp_bot.models.whatsapp import WhatsAppTemplate

class Command(BaseCommand):
    help = 'Setup default WhatsApp message templates'

    def handle(self, *args, **options):
        self.stdout.write('Setting up default WhatsApp templates...')
        
        templates = [
            {
                'template_type': 'appointment_schedule_patient',
                'subject': 'Appointment Confirmed',
                'content': """🏥 *CARE - Appointment Confirmed*

Hello {{ patient_name }},

Your appointment has been successfully scheduled!

📅 *Date:* {{ appointment_date }}
⏰ *Time:* {{ appointment_time }}
📍 *Location:* {{ location }}
👨‍⚕️ *Doctor:* Dr. {{ practitioner_name }}

Please arrive 15 minutes early for check-in.

For any changes or queries, please contact us.

Thank you for choosing CARE! 🙏""",
                'variables': {
                    'patient_name': 'Patient name',
                    'appointment_date': 'Appointment date',
                    'appointment_time': 'Appointment time',
                    'location': 'Location/facility name',
                    'practitioner_name': 'Doctor name'
                }
            },
            {
                'template_type': 'appointment_schedule_practitioner',
                'subject': 'New Appointment',
                'content': """🏥 *CARE - New Appointment*

Hello Dr. {{ practitioner_name }},

You have a new appointment scheduled:

👤 *Patient:* {{ patient_name }}
📅 *Date:* {{ appointment_date }}
⏰ *Time:* {{ appointment_time }}
📍 *Location:* {{ location }}

Please review your schedule accordingly.

CARE System 🏥""",
                'variables': {
                    'practitioner_name': 'Doctor name',
                    'patient_name': 'Patient name',
                    'appointment_date': 'Appointment date',
                    'appointment_time': 'Appointment time',
                    'location': 'Location/facility name'
                }
            },
            {
                'template_type': 'appointment_reschedule_patient',
                'subject': 'Appointment Rescheduled',
                'content': """🔄 *CARE - Appointment Rescheduled*

Hello {{ patient_name }},

Your appointment has been rescheduled:

📋 *Previous Appointment:*
📅 Date: {{ original_date }}
⏰ Time: {{ original_time }}

📋 *New Appointment:*
📅 Date: {{ new_date }}
⏰ Time: {{ new_time }}
📍 Location: {{ location }}

Please make note of the new date and time.
Arrive 15 minutes early for check-in.

For any questions, please contact us.

Thank you for your understanding! 🙏""",
                'variables': {
                    'patient_name': 'Patient name',
                    'original_date': 'Previous appointment date',
                    'original_time': 'Previous appointment time',
                    'new_date': 'New appointment date',
                    'new_time': 'New appointment time',
                    'location': 'Location/facility name'
                }
            },
            {
                'template_type': 'appointment_reschedule_practitioner',
                'subject': 'Appointment Rescheduled',
                'content': """🔄 *CARE - Appointment Rescheduled*

Hello Dr. {{ practitioner_name }},

An appointment has been rescheduled:

👤 *Patient:* {{ patient_name }}

📋 *Previous:*
📅 Date: {{ original_date }}
⏰ Time: {{ original_time }}

📋 *New Schedule:*
📅 Date: {{ new_date }}
⏰ Time: {{ new_time }}
📍 Location: {{ location }}

Please update your calendar accordingly.

CARE System 🏥""",
                'variables': {
                    'practitioner_name': 'Doctor name',
                    'patient_name': 'Patient name',
                    'original_date': 'Previous appointment date',
                    'original_time': 'Previous appointment time',
                    'new_date': 'New appointment date',
                    'new_time': 'New appointment time',
                    'location': 'Location/facility name'
                }
            },
            {
                'template_type': 'discharge_summary_patient',
                'subject': 'Discharge Summary',
                'content': """🏥 *CARE - Discharge Summary*

Hello {{ patient_name }},

Your discharge summary is ready:

🏥 *Hospital:* {{ hospital_name }}
👨‍⚕️ *Doctor:* Dr. {{ doctor_name }}
📅 *Discharge Date:* {{ discharge_date }}

📋 *Summary:*
{{ summary }}

Please keep this information for your records.

Thank you for choosing CARE! 🙏""",
                'variables': {
                    'patient_name': 'Patient name',
                    'hospital_name': 'Hospital name',
                    'doctor_name': 'Doctor name',
                    'discharge_date': 'Discharge date',
                    'summary': 'Discharge summary'
                }
            },
            {
                'template_type': 'welcome_message',
                'subject': 'Welcome to CARE',
                'content': """🏥 *Welcome to CARE, {{ patient_name }}!*

I'm your healthcare assistant. Here's what I can help you with:

1️⃣ *View Appointments* - Check your upcoming appointments
2️⃣ *About Care* - Learn more about CARE

Reply with the number or text to get started!

CARE - Your Health, Our Priority 💙""",
                'variables': {
                    'patient_name': 'Patient name'
                }
            },
            {
                'template_type': 'appointments_list',
                'subject': 'Your Appointments',
                'content': """📅 *Your Upcoming Appointments*

You have {{ appointments_count }} appointment(s):

{% for appointment in appointments_list %}
📅 *{{ appointment.date }}*
⏰ Time: {{ appointment.time }}
📍 Location: {{ appointment.location }}
👨‍⚕️ Doctor: {{ appointment.practitioner }}

{% endfor %}

Thank you for choosing CARE! 🙏""",
                'variables': {
                    'appointments_count': 'Number of appointments',
                    'appointments_list': 'List of appointment details'
                }
            },
            {
                'template_type': 'about_care',
                'subject': 'About CARE',
                'content': """🏥 *About CARE*

CARE is your comprehensive healthcare management system that connects patients, doctors, and healthcare facilities seamlessly.

🌐 *Visit us:* https://ohc.network
📞 *Contact:* +1-800-CARE-HELP
📧 *Email:* support@care.health

*Our Mission:*
To provide accessible, efficient, and personalized healthcare services to everyone.

*Features:*
• Easy appointment booking
• Digital health records
• Secure messaging
• Telemedicine consultations
• Prescription management

CARE - Your Health, Our Priority 💙""",
                'variables': {}
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            template, created = WhatsAppTemplate.objects.update_or_create(
                template_type=template_data['template_type'],
                defaults={
                    'subject': template_data['subject'],
                    'content': template_data['content'],
                    'variables': template_data['variables'],
                    'is_enabled': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✅ Created template: {template.template_type}')
            else:
                updated_count += 1
                self.stdout.write(f'🔄 Updated template: {template.template_type}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully setup {created_count} new templates and updated {updated_count} existing templates!'
            )
        ) 