from typing import Any

import environ
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.dispatch import receiver
from rest_framework.settings import perform_import

from care_whatsapp_bot.apps import PLUGIN_NAME

env = environ.Env()


class PluginSettings:  # pragma: no cover
    """
    A settings object that allows plugin settings to be accessed as
    properties. For example:

        from plugin.settings import plugin_settings
        print(plugin_settings.API_KEY)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.

    """

    def __init__(
        self,
        plugin_name: str = None,
        defaults: dict | None = None,
        import_strings: set | None = None,
        required_settings: set | None = None,
    ) -> None:
        if not plugin_name:
            raise ValueError("Plugin name must be provided")
        self.plugin_name = plugin_name
        self.defaults = defaults or {}
        self.import_strings = import_strings or set()
        self.required_settings = required_settings or set()
        self._cached_attrs = set()
        self.validate()

    def __getattr__(self, attr) -> Any:
        if attr not in self.defaults:
            raise AttributeError("Invalid setting: '%s'" % attr)

        # Try to find the setting from user settings, then from environment variables
        val = self.defaults[attr]
        try:
            val = self.user_settings[attr]
        except KeyError:
            try:
                val = env(attr, cast=type(val))
            except environ.ImproperlyConfigured:
                # Fall back to defaults
                pass

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    @property
    def user_settings(self) -> dict:
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "PLUGIN_CONFIGS", {}).get(
                self.plugin_name, {}
            )
        return self._user_settings

    def validate(self) -> None:
        """
        This method handles the validation of the plugin settings.
        It could be overridden to provide custom validation logic.

        the base implementation checks if all the required settings are truthy.
        """
        for setting in self.required_settings:
            if not getattr(self, setting):
                raise ImproperlyConfigured(
                    f'The "{setting}" setting is required. '
                    f'Please set the "{setting}" in the environment or the {PLUGIN_NAME} plugin config.'
                )

    def reload(self) -> None:
        """
        Deletes the cached attributes so they will be recomputed next time they are accessed.
        """
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


REQUIRED_SETTINGS = {
    "WHATSAPP_ACCESS_TOKEN",
    "WHATSAPP_PHONE_NUMBER_ID",
    "WHATSAPP_WEBHOOK_VERIFY_TOKEN",
    "WHATSAPP_WEBHOOK_SECRET",
}

DEFAULTS = {
    # WhatsApp Business API Configuration
    "WHATSAPP_ACCESS_TOKEN": "",
    "WHATSAPP_PHONE_NUMBER_ID": "",
    "WHATSAPP_WEBHOOK_VERIFY_TOKEN": "care_whatsapp_bot_verify",
    "WHATSAPP_WEBHOOK_SECRET": "",
    "WHATSAPP_API_VERSION": "v18.0",
    "WHATSAPP_BASE_URL": "https://graph.facebook.com",
    
    # Bot Configuration
    "BOT_NAME": "CARE Assistant",
    "BOT_WELCOME_MESSAGE": "Welcome to CARE! I'm here to help you with your healthcare needs. Type 'help' to see available commands.",
    "BOT_HELP_MESSAGE": "Available commands:\n- login: Authenticate with your credentials\n- records: View your medical records\n- appointments: View your appointments\n- medications: View your medications\n- help: Show this help message\n- logout: End your session",
    
    # Session Configuration
    "SESSION_TIMEOUT_MINUTES": 30,
    "MAX_RETRY_ATTEMPTS": 3,
    "RATE_LIMIT_MESSAGES_PER_MINUTE": 10,
    
    # Privacy and Security
    "ENABLE_MESSAGE_ENCRYPTION": False,
    "LOG_SENSITIVE_DATA": False,
    "REQUIRE_PHONE_VERIFICATION": True,
    
    # Media Handling
    "MAX_FILE_SIZE_MB": 16,
    "ALLOWED_FILE_TYPES": ["pdf", "jpg", "jpeg", "png", "doc", "docx"],
    "MEDIA_STORAGE_PATH": "/tmp/whatsapp_media",
    
    # Notification Settings
    "ENABLE_APPOINTMENT_REMINDERS": True,
    "ENABLE_MEDICATION_REMINDERS": True,
    "REMINDER_ADVANCE_HOURS": 24,
    
    # Development Settings
    "DEBUG_WEBHOOK": False,
    "MOCK_WHATSAPP_API": False,
    "TEST_PHONE_NUMBERS": [],
    
    # Legacy settings for backward compatibility
    "CARE_WHATSAPP_BOT_API_KEY": "",
    "CARE_WHATSAPP_BOT_WEBHOOK_URL": "",
    "CARE_WHATSAPP_BOT_VERIFY_TOKEN": "care_whatsapp_bot_verify",
}

plugin_settings = PluginSettings(
    PLUGIN_NAME, defaults=DEFAULTS, required_settings=REQUIRED_SETTINGS
)


@receiver(setting_changed)
def reload_plugin_settings(*args, **kwargs) -> None:
    setting = kwargs["setting"]
    if setting == "PLUGIN_CONFIGS":
        plugin_settings.reload()
