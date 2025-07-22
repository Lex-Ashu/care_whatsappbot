from rest_framework.routers import DefaultRouter
from django.urls import path

from care_whatsapp_bot.api.viewsets.whatsapp import CareWhatsappBotViewset
from care_whatsapp_bot.api.viewsets.whatsapp import WhatsAppWebhookView

router = DefaultRouter()

router.register("whatsapp", CareWhatsappBotViewset, basename="care_whatsapp_bot__whatsapp")

urlpatterns = router.urls + [
    path('webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
]
