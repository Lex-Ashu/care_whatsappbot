from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class WhatsAppMessage(models.Model):
    MESSAGE_TYPES = [
        ('appointment_schedule', 'Appointment Schedule'),
        ('appointment_reschedule', 'Appointment Reschedule'),
        ('discharge_summary', 'Discharge Summary'),
        ('welcome', 'Welcome Message'),
        ('appointments_list', 'Appointments List'),
        ('about_care', 'About Care'),
        ('menu', 'Menu'),
        ('error', 'Error Message'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    recipient_phone = models.CharField(max_length=20)
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    whatsapp_message_id = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Tracking timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    template_used = models.CharField(max_length=50, blank=True, null=True)
    variables_used = models.JSONField(default=dict, blank=True)
    retry_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'care_whatsapp_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient_phone', 'status']),
            models.Index(fields=['whatsapp_message_id']),
            models.Index(fields=['message_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.message_type} to {self.recipient_phone} - {self.status}"
    
    def mark_sent(self, whatsapp_message_id=None):
        """Mark message as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if whatsapp_message_id:
            self.whatsapp_message_id = whatsapp_message_id
        self.save(update_fields=['status', 'sent_at', 'whatsapp_message_id', 'updated_at'])
    
    def mark_delivered(self):
        """Mark message as delivered"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])
    
    def mark_read(self):
        """Mark message as read"""
        self.status = 'read'
        self.read_at = timezone.now()
        self.save(update_fields=['status', 'read_at', 'updated_at'])
    
    def mark_failed(self, error_message=None):
        """Mark message as failed"""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])

class WhatsAppTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('appointment_schedule_patient', 'Appointment Schedule - Patient'),
        ('appointment_schedule_practitioner', 'Appointment Schedule - Practitioner'),
        ('appointment_reschedule_patient', 'Appointment Reschedule - Patient'),
        ('appointment_reschedule_practitioner', 'Appointment Reschedule - Practitioner'),
        ('discharge_summary_patient', 'Discharge Summary - Patient'),
        ('welcome_message', 'Welcome Message'),
        ('appointments_list', 'Appointments List'),
        ('about_care', 'About Care'),
        ('menu', 'Menu'),
        ('error_message', 'Error Message'),
    ]
    
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES, unique=True)
    is_enabled = models.BooleanField(default=True)
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    variables = models.JSONField(default=dict, help_text="Available variables for this template")
    
    # Media support
    has_image = models.BooleanField(default=False)
    image_url = models.URLField(blank=True, null=True)
    image_caption = models.TextField(blank=True)
    
    # Button support
    has_buttons = models.BooleanField(default=False)
    buttons = models.JSONField(default=list, help_text="List of buttons for interactive messages")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'care_whatsapp_templates'
    
    def __str__(self):
        return f"{self.template_type} - {'Enabled' if self.is_enabled else 'Disabled'}"
    
    def get_available_variables(self):
        """Get list of available variables for this template"""
        return list(self.variables.keys()) if self.variables else []

class WhatsAppConfiguration(models.Model):
    NOTIFICATION_TYPES = [
        ('appointment_schedule', 'Appointment Schedule Notifications'),
        ('appointment_reschedule', 'Appointment Reschedule Notifications'),
        ('discharge_summary', 'Discharge Summary Notifications'),
        ('welcome_message', 'Welcome Messages'),
        ('delivery_receipts', 'Delivery Receipt Tracking'),
        ('read_receipts', 'Read Receipt Tracking'),
    ]
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'care_whatsapp_config'
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['notification_type', 'is_enabled']),
        ]
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}..."
    
    @classmethod
    def is_notification_enabled(cls, notification_type):
        """Check if a notification type is enabled"""
        try:
            config = cls.objects.get(key=f"{notification_type}_enabled")
            return config.is_enabled and config.value.lower() == 'true'
        except cls.DoesNotExist:
            return True  # Default to enabled if not configured

class WhatsAppInboundMessage(models.Model):
    """Track inbound messages from patients"""
    sender_phone = models.CharField(max_length=20)
    message_content = models.TextField()
    whatsapp_message_id = models.CharField(max_length=100, unique=True)
    
    # Processing status
    is_processed = models.BooleanField(default=False)
    response_sent = models.BooleanField(default=False)
    
    # Patient linking
    patient = models.ForeignKey('care.patient.models.Patient', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'care_whatsapp_inbound_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender_phone', 'created_at']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        return f"Inbound from {self.sender_phone}: {self.message_content[:50]}..."
    
    def mark_processed(self):
        """Mark message as processed"""
        self.is_processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['is_processed', 'processed_at'])

class WhatsAppDeliveryStatus(models.Model):
    """Track delivery and read status updates from WhatsApp"""
    whatsapp_message_id = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, choices=WhatsAppMessage.STATUS_CHOICES)
    timestamp = models.DateTimeField()
    
    # Related message
    message = models.ForeignKey(WhatsAppMessage, on_delete=models.CASCADE, related_name='delivery_statuses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'care_whatsapp_delivery_status'
        ordering = ['-timestamp']
        unique_together = ['whatsapp_message_id', 'status']
    
    def __str__(self):
        return f"{self.whatsapp_message_id} - {self.status} at {self.timestamp}"