from ebay.listing.views import EbayListingViewSet
from rest_framework.routers import DefaultRouter

app_name = "listing"

# Create default router
router = DefaultRouter()


# Create routes for EbayListingViewSet
router.register(r"", EbayListingViewSet, basename="listing")


# Create urlpatterns
urlpatterns = router.urls
