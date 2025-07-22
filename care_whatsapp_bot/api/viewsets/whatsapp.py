from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpRequest
from care_whatsapp_bot.message_router import MessageRouter

class WhatsAppWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        try:
            msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = msg["from"]
            text = msg["text"]["body"]
            MessageRouter().route(sender, text)
        except Exception:
            pass
        return Response("OK") 