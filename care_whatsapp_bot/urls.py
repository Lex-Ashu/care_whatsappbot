from rest_framework.routers import DefaultRouter

from care_whatsapp_bot.api.viewsets.whatsapp import CareWhatsappBotViewset

router = DefaultRouter()

router.register("whatsapp", CareWhatsappBotViewset, basename="care_whatsapp_bot__whatsapp")

urlpatterns = router.urls
