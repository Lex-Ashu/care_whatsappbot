from django.contrib import admin
from django.utils.html import format_html
from care_whatsapp_bot.models.whatsapp import WhatsAppMessage, WhatsAppTemplate, WhatsAppConfiguration

@admin.register(WhatsAppTemplate)
class WhatsAppTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_type', 'is_enabled', 'subject', 'created_at', 'updated_at']
    list_filter = ['is_enabled', 'template_type', 'created_at']
    search_fields = ['template_type', 'subject', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('template_type', 'is_enabled', 'subject')
        }),
        ('Content', {
            'fields': ('content', 'variables'),
            'description': 'Use Django template syntax with variables like {{ variable_name }}'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('template_type',)
        return self.readonly_fields

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ['recipient_phone', 'message_type', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'message_type', 'created_at', 'sent_at']
    search_fields = ['recipient_phone', 'content']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('recipient_phone', 'message_type', 'status')
        }),
        ('Content', {
            'fields': ('content', 'error_message')
        }),
        ('WhatsApp Details', {
            'fields': ('whatsapp_message_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        return False  # Messages are created automatically by the system
    
    def has_change_permission(self, request, obj=None):
        return False  # Messages should not be manually edited
    
    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletion for cleanup

@admin.register(WhatsAppConfiguration)
class WhatsAppConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'description', 'updated_at']
    search_fields = ['key', 'value', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def value_preview(self, obj):
        """Show a preview of the value"""
        if len(obj.value) > 50:
            return format_html('<span title="{}">{}</span>', obj.value, obj.value[:50] + '...')
        return obj.value
    value_preview.short_description = 'Value'
    
    fieldsets = (
        ('Configuration', {
            'fields': ('key', 'value', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    ) 