from django.urls import path
from django.http import HttpResponse
from django.views import View
import requests

from care_whatsapp_bot.api.viewsets.whatsapp import WhatsAppWebhookView

class WebhookProxyView(View):
    def post(self, request, *args, **kwargs):
        try:
            response = requests.post(
                'http://localhost:8000/api/care_whatsapp_bot/webhook/',
                data=request.body,
                headers=request.headers,
                timeout=10
            )
            return HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('content-type', 'application/json')
            )
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)
    
    def get(self, request, *args, **kwargs):
        try:
            response = requests.get(
                'http://localhost:8000/api/care_whatsapp_bot/webhook/',
                params=request.GET,
                headers=request.headers,
                timeout=10
            )
            return HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('content-type', 'application/json')
            )
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)

urlpatterns = [
    path('webhook/', WebhookProxyView.as_view(), name='whatsapp-webhook-proxy'),
    path('api/care_whatsapp_bot/webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
]
