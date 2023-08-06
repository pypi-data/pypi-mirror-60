from django.urls import path

from etsy.account import views
from etsy.account.views import EtsyUserAccountAuthUrl
from rest_framework.routers import DefaultRouter

app_name = "account"


urlpatterns = [
    path("get_auth_url", EtsyUserAccountAuthUrl.as_view(), name="get_auth_url"),
]


router = DefaultRouter()
router.register("", views.EtsyUserAccountViewSet, basename="user_account")


urlpatterns += router.urls
