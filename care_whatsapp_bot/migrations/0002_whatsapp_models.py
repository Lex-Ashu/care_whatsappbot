# Generated migration for WhatsApp Bot models

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('care_whatsapp_bot', '0001_initial'),
    ]

    operations = [
        # Remove old Hello model
        migrations.DeleteModel(
            name='Hello',
        ),
        
        # Create WhatsAppSession model
        migrations.CreateModel(
            name='WhatsAppSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(db_index=True, max_length=20, unique=True)),
                ('user_type', models.CharField(choices=[('patient', 'Patient'), ('staff', 'Staff'), ('unknown', 'Unknown')], default='unknown', max_length=20)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('is_authenticated', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'WhatsApp Session',
                'verbose_name_plural': 'WhatsApp Sessions',
                'db_table': 'care_whatsapp_bot_session',
            },
        ),
        
        # Create WhatsAppMessage model
        migrations.CreateModel(
            name='WhatsAppMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(choices=[('incoming', 'Incoming'), ('outgoing', 'Outgoing')], max_length=10)),
                ('message_type', models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('document', 'Document'), ('audio', 'Audio'), ('video', 'Video'), ('location', 'Location'), ('interactive', 'Interactive')], max_length=20)),
                ('content', models.TextField()),
                ('whatsapp_message_id', models.CharField(blank=True, max_length=100, null=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='care_whatsapp_bot.whatsappsession')),
            ],
            options={
                'verbose_name': 'WhatsApp Message',
                'verbose_name_plural': 'WhatsApp Messages',
                'db_table': 'care_whatsapp_bot_message',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create WhatsAppCommand model
        migrations.CreateModel(
            name='WhatsAppCommand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('command_type', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('get_records', 'Get Medical Records'), ('get_medications', 'Get Medications'), ('get_appointments', 'Get Appointments'), ('get_procedures', 'Get Procedures'), ('get_test_results', 'Get Test Results'), ('schedule_appointment', 'Schedule Appointment'), ('cancel_appointment', 'Cancel Appointment')], max_length=50)),
                ('command_data', models.JSONField(blank=True, default=dict)),
                ('is_successful', models.BooleanField(default=False)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('executed_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commands', to='care_whatsapp_bot.whatsappsession')),
            ],
            options={
                'verbose_name': 'WhatsApp Command',
                'verbose_name_plural': 'WhatsApp Commands',
                'db_table': 'care_whatsapp_bot_command',
                'ordering': ['-executed_at'],
            },
        ),
        
        # Create WhatsAppNotification model
        migrations.CreateModel(
            name='WhatsAppNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_id', models.IntegerField()),
                ('notification_type', models.CharField(choices=[('appointment_reminder', 'Appointment Reminder'), ('medication_reminder', 'Medication Reminder'), ('test_result_available', 'Test Result Available'), ('discharge_summary', 'Discharge Summary'), ('general_notification', 'General Notification')], max_length=50)),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('scheduled_at', models.DateTimeField()),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'WhatsApp Notification',
                'verbose_name_plural': 'WhatsApp Notifications',
                'db_table': 'care_whatsapp_bot_notification',
                'ordering': ['-created_at'],
            },
        ),
        
        # Add indexes for better performance
        migrations.AddIndex(
            model_name='whatsappmessage',
            index=models.Index(fields=['session', 'created_at'], name='care_whatsapp_bot_message_session_created_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappmessage',
            index=models.Index(fields=['whatsapp_message_id'], name='care_whatsapp_bot_message_whatsapp_id_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappcommand',
            index=models.Index(fields=['session', 'command_type'], name='care_whatsapp_bot_command_session_type_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappnotification',
            index=models.Index(fields=['patient_id', 'status'], name='care_whatsapp_bot_notification_patient_status_idx'),
        ),
        migrations.AddIndex(
            model_name='whatsappnotification',
            index=models.Index(fields=['scheduled_at', 'status'], name='care_whatsapp_bot_notification_scheduled_status_idx'),
        ),
    ]