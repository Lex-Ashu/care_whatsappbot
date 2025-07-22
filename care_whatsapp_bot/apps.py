from django.apps import AppConfig

class CareWhatsappBotConfig(AppConfig):
    name = "care_whatsapp_bot"

    def ready(self):
        import care_whatsapp_bot.signals 