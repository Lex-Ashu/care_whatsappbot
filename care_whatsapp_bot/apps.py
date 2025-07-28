from django.apps import AppConfig

PLUGIN_NAME = "care_whatsapp_bot"

class CareWhatsappBotConfig(AppConfig):
    name = "care_whatsapp_bot"

    def ready(self):
        import care_whatsapp_bot.signals