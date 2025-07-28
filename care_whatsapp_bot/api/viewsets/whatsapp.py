import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpRequest
from care_whatsapp_bot.message_router import MessageRouter
from care_whatsapp_bot.services.whatsapp_notification_service import WhatsAppNotificationService

logger = logging.getLogger(__name__)

class WhatsAppWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        logger.info(f"📥 Received webhook data: {data}")
        
        try:
            entry = data.get("entry", [])
            if not entry:
                logger.warning("No entry found in webhook data")
                return Response("OK")
            
            changes = entry[0].get("changes", [])
            if not changes:
                logger.warning("No changes found in webhook data")
                return Response("OK")
            
            value = changes[0].get("value", {})
            
            # Handle status updates
            if "statuses" in value:
                self._handle_status_updates(value["statuses"])
            
            # Handle incoming messages
            if "messages" in value:
                self._handle_incoming_messages(value["messages"])
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            
        return Response("OK")
    
    def _handle_status_updates(self, statuses):
        """Handle message status updates"""
        notification_service = WhatsAppNotificationService()
        
        for status in statuses:
            try:
                message_id = status.get("id")
                status_type = status.get("status")
                timestamp = status.get("timestamp")
                
                if message_id and status_type:
                    logger.info(f"📊 Status update: {message_id} -> {status_type}")
                    notification_service.update_message_status(message_id, status_type, timestamp)
                    
            except Exception as e:
                logger.error(f"Error handling status update: {str(e)}")
    
    def _handle_incoming_messages(self, messages):
        """Handle incoming messages"""
        router = MessageRouter()
        
        for message in messages:
            try:
                sender = message.get("from")
                message_type = message.get("type")
                
                if message_type == "text":
                    text = message.get("text", {}).get("body", "")
                    logger.info(f"📨 Incoming text message from {sender}: {text}")
                    router.route(sender, text)
                else:
                    logger.info(f"📨 Incoming {message_type} message from {sender}")
                    
            except Exception as e:
                logger.error(f"Error handling incoming message: {str(e)}") 