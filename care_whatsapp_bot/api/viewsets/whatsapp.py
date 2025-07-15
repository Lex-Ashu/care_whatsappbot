import json
import logging
from typing import Dict, Any

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from care_whatsapp_bot.api.serializers.whatsapp import (
    WhatsappConversationSerializer,
    WhatsappMessageSerializer,
    WhatsappWebhookSerializer
)
from care_whatsapp_bot.models.whatsapp import WhatsAppSession, WhatsAppMessage
from care_whatsapp_bot.im_wrapper.whatsapp import WhatsAppProvider
from care_whatsapp_bot.message_router import MessageRouter
from care_whatsapp_bot.utils.data_formatter import DataFormatter

logger = logging.getLogger(__name__)


class CareWhatsappBotViewset(
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    GenericViewSet
):
    queryset = WhatsAppSession.objects.all().order_by("-created_at")
    serializer_class = WhatsappConversationSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.whatsapp_provider = WhatsAppProvider({})
        self.message_router = MessageRouter()
        self.formatter = DataFormatter()
    
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['get', 'post'], permission_classes=[])
    def webhook(self, request):
        """Handle WhatsApp webhook requests"""
        if request.method == 'GET':
            return self._handle_webhook_verification(request)
        elif request.method == 'POST':
            return self._handle_incoming_message(request)
    
    def _handle_webhook_verification(self, request):
        """Handle webhook verification"""
        try:
            mode = request.GET.get('hub.mode')
            token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')
            
            logger.info(f"Webhook verification request: mode={mode}, token={token}")
            
            response_challenge = self.whatsapp_provider.verify_webhook(mode, token, challenge)
            
            if response_challenge:
                logger.info("Webhook verification successful")
                return HttpResponse(response_challenge, content_type='text/plain')
            else:
                logger.warning("Webhook verification failed")
                return HttpResponseForbidden("Verification failed")
        
        except Exception as e:
            logger.error(f"Error in webhook verification: {e}")
            return HttpResponseBadRequest("Verification error")
    
    def _handle_incoming_message(self, request):
        """Handle incoming WhatsApp messages"""
        try:
            body = request.body.decode('utf-8')
            signature = request.headers.get('X-Hub-Signature-256', '')
            
            # Validate webhook signature
            if not self.whatsapp_provider.validate_webhook_signature(body, signature):
                logger.warning("Invalid webhook signature")
                return HttpResponseForbidden("Invalid signature")
            
            try:
                payload = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {e}")
                return HttpResponseBadRequest("Invalid JSON")
            
            # Process webhook
            self._process_webhook(payload)
            
            return HttpResponse("OK", content_type='text/plain')
        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return HttpResponse("OK", content_type='text/plain')  # Always return OK to WhatsApp
    
    def _process_webhook(self, payload: Dict[str, Any]) -> None:
        """Process incoming webhook payload"""
        try:
            incoming_message = self.whatsapp_provider.parse_incoming_message(payload)
            
            if not incoming_message:
                logger.info("No message to process in webhook payload")
                return
            
            logger.info(f"Processing message from {incoming_message.sender_id}: {incoming_message.content[:100]}")
            
            # Route message and get responses
            responses = self.message_router.route_message(incoming_message)
            
            # Send responses
            for response in responses:
                try:
                    success = self.whatsapp_provider.send_message(response)
                    if success:
                        logger.info(f"Response sent to {response.recipient_id}")
                    else:
                        logger.error(f"Failed to send response to {response.recipient_id}")
                except Exception as e:
                    logger.error(f"Error sending response: {e}")
        
        except Exception as e:
            logger.error(f"Error processing webhook payload: {e}")
    
    @action(detail=False, methods=['get'], permission_classes=[])
    def health_check(self, request):
        """Health check endpoint for the WhatsApp bot"""
        try:
            health_status = {
                'status': 'healthy',
                'service': 'CARE WhatsApp Bot',
                'version': '1.0.0'
            }
            
            if not self.whatsapp_provider.access_token:
                health_status['warnings'] = ['WhatsApp access token not configured']
            
            return Response(health_status, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return Response({
                'status': 'unhealthy',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def send_test_message(self, request):
        """Test endpoint to send a message (for development/testing)"""
        try:
            from django.conf import settings
            if not settings.DEBUG:
                return Response(
                    {"error": "Not available in production"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            phone_number = request.data.get('phone_number')
            message = request.data.get('message')
            
            if not phone_number or not message:
                return Response(
                    {"error": "phone_number and message are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from care_whatsapp_bot.im_wrapper.base import IMResponse, MessageType
            
            response = IMResponse(
                recipient_id=phone_number,
                message_type=MessageType.TEXT,
                content=message
            )
            
            success = self.whatsapp_provider.send_message(response)
            
            return Response({
                'success': success,
                'message': 'Test sent' if success else 'Test failed'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error sending test message: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
