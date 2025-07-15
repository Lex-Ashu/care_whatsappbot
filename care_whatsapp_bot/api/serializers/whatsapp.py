from rest_framework import serializers
from care_whatsapp_bot.models.whatsapp import (
    WhatsAppSession, 
    WhatsAppMessage, 
    WhatsAppCommand, 
    WhatsAppNotification
)


class WhatsappConversationSerializer(serializers.ModelSerializer):
    """Serializer for WhatsApp sessions (conversations)"""
    
    class Meta:
        model = WhatsAppSession
        fields = [
            'id', 'phone_number', 'user_type', 'user_id', 'is_authenticated', 
            'is_active', 'last_activity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WhatsappMessageSerializer(serializers.ModelSerializer):
    """Serializer for WhatsApp messages"""
    
    session = WhatsappConversationSerializer(read_only=True)
    
    class Meta:
        model = WhatsAppMessage
        fields = [
            'id', 'session', 'direction', 'message_type', 'content', 
            'whatsapp_message_id', 'is_processed', 'processed_at', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WhatsAppCommandSerializer(serializers.ModelSerializer):
    """Serializer for WhatsApp commands"""
    
    session = WhatsappConversationSerializer(read_only=True)
    
    class Meta:
        model = WhatsAppCommand
        fields = [
            'id', 'session', 'command_type', 'command_data', 'is_successful', 
            'error_message', 'executed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WhatsAppNotificationSerializer(serializers.ModelSerializer):
    """Serializer for WhatsApp notifications"""
    
    class Meta:
        model = WhatsAppNotification
        fields = [
            'id', 'patient_id', 'notification_type', 'content', 'status', 
            'scheduled_at', 'sent_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WhatsappWebhookSerializer(serializers.Serializer):
    """Serializer for incoming WhatsApp webhook data"""
    
    phone_number = serializers.CharField(max_length=20)
    message_text = serializers.CharField()
    message_id = serializers.CharField()
    timestamp = serializers.DateTimeField()
    message_type = serializers.CharField(max_length=20, default='text')
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        import re
        # Basic phone number validation
        if not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
