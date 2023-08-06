from rest_framework.routers import DefaultRouter

from zonesmart.news.views import AnnouncementViewSet

app_name = "zonesmart.news"


router = DefaultRouter()
router.register(r"", AnnouncementViewSet, basename="announcement")


urlpatterns = router.urls
