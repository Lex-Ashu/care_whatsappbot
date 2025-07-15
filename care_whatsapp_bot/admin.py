from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models.whatsapp import (
    WhatsAppSession,
    WhatsAppMessage,
    WhatsAppCommand,
    WhatsAppNotification
)


@admin.register(WhatsAppSession)
class WhatsAppSessionAdmin(admin.ModelAdmin):
    list_display = [
        'phone_number',
        'user_type',
        'is_authenticated',
        'last_activity',
        'session_status',
        'created_at'
    ]
    list_filter = [
        'user_type',
        'is_authenticated',
        'created_at',
        'last_activity'
    ]
    search_fields = ['phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('phone_number', 'user_type')
        }),
        ('User Links', {
            'fields': ('user_id',)
        }),
        ('Session Status', {
            'fields': (
                'is_authenticated',
                'is_active',
                'last_activity'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def session_status(self, obj):
        if obj.is_active and obj.is_authenticated:
            return format_html(
                '<span style="color: green;">✓ Active</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: orange;">⚠ Not Authenticated</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Inactive</span>'
            )
    session_status.short_description = 'Status'


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = [
        'session_phone',
        'direction',
        'message_type',
        'content_preview',
        'is_processed',
        'created_at'
    ]
    list_filter = [
        'direction',
        'message_type',
        'is_processed',
        'created_at'
    ]
    search_fields = ['session__phone_number', 'content']
    readonly_fields = [
        'whatsapp_message_id',
        'created_at',
        'updated_at',
        'processed_at'
    ]
    
    fieldsets = (
        ('Message Information', {
            'fields': (
                'whatsapp_message_id',
                'session',
                'direction',
                'message_type'
            )
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Processing', {
            'fields': (
                'is_processed',
                'processed_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def session_phone(self, obj):
        return obj.session.phone_number if obj.session else 'N/A'
    session_phone.short_description = 'Phone Number'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')


@admin.register(WhatsAppCommand)
class WhatsAppCommandAdmin(admin.ModelAdmin):
    list_display = [
        'session_phone',
        'command_type',
        'is_successful',
        'executed_at'
    ]
    list_filter = [
        'command_type',
        'is_successful',
        'executed_at'
    ]
    search_fields = ['session__phone_number']
    readonly_fields = ['executed_at', 'created_at']
    
    fieldsets = (
        ('Command Information', {
            'fields': (
                'session',
                'command_type',
                'command_data'
            )
        }),
        ('Execution Details', {
            'fields': (
                'is_successful',
                'error_message'
            )
        }),
        ('Timestamps', {
            'fields': ('executed_at', 'created_at')
        })
    )
    
    def session_phone(self, obj):
        return obj.session.phone_number if obj.session else 'N/A'
    session_phone.short_description = 'Phone Number'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session')


@admin.register(WhatsAppNotification)
class WhatsAppNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'patient_id',
        'notification_type',
        'status',
        'scheduled_at',
        'sent_at'
    ]
    list_filter = [
        'notification_type',
        'status',
        'scheduled_at',
        'sent_at'
    ]
    search_fields = ['patient_id', 'content']
    readonly_fields = [
        'sent_at',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Notification Information', {
            'fields': (
                'patient_id',
                'notification_type',
                'content'
            )
        }),
        ('Scheduling', {
            'fields': (
                'status',
                'scheduled_at',
                'sent_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


# Custom admin site configuration
admin.site.site_header = "CARE WhatsApp Bot Administration"
admin.site.site_title = "WhatsApp Bot Admin"
admin.site.index_title = "Welcome to CARE WhatsApp Bot Administration"