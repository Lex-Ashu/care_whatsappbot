from django.urls import path

from care_whatsapp_bot.api.viewsets.whatsapp import WhatsAppWebhookView

urlpatterns = [
    path('webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
]
