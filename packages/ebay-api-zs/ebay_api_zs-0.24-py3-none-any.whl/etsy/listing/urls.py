from etsy.listing.views.listing import EtsyListingViewSet
from rest_framework.routers import SimpleRouter


app_name = "etsy.listing"


router = SimpleRouter()
router.register("", EtsyListingViewSet, basename="listing")


urlpatterns = router.urls
