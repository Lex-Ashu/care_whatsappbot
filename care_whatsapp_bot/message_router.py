from care_whatsapp_bot.im_wrapper.whatsapp import WhatsAppProvider
from care_whatsapp_bot.im_wrapper.base import IMResponse, MessageType
from care_whatsapp_bot.settings import plugin_settings

class MessageRouter:
    def __init__(self):
        self.whatsapp = WhatsAppProvider({
            'access_token': plugin_settings.WHATSAPP_ACCESS_TOKEN,
            'phone_number_id': plugin_settings.WHATSAPP_PHONE_NUMBER_ID,
        })

    def route(self, sender, text):
        text = text.strip().lower()
        if text in ["view appointments", "appointments"]:
            return self._handle_view_appointments(sender)
        elif text in ["about care", "about"]:
            return self._handle_about_care(sender)
        else:
            return self._handle_menu(sender)

    def _handle_menu(self, sender):
        msg = "Welcome to CARE!\n1. View Appointments\n2. About Care\nReply with the option."
        response = IMResponse(
            recipient_id=sender,
            message_type=MessageType.TEXT,
            content=msg
        )
        self.whatsapp.send_message(response)

    def _handle_view_appointments(self, sender):
        # Placeholder: Replace with real appointment fetch logic
        msg = "You have no upcoming appointments."
        response = IMResponse(
            recipient_id=sender,
            message_type=MessageType.TEXT,
            content=msg
        )
        self.whatsapp.send_message(response)

    def _handle_about_care(self, sender):
        msg = "CARE is your digital healthcare companion. Visit https://ohc.network for more."
        response = IMResponse(
            recipient_id=sender,
            message_type=MessageType.TEXT,
            content=msg
        )
        self.whatsapp.send_message(response)