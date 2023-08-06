from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from zonesmart.support import views

app_name = "zonesmart.support"

router = DefaultRouter()

# Support request urls
router.register(
    r"support_request", views.SupportRequestViewSet, basename="support_request"
)
# Support request message urls
support_request_message_router = NestedDefaultRouter(
    router, r"support_request", lookup="support_request"
)
support_request_message_router.register(
    r"message", views.SupportRequestMessageViewSet, basename="message"
)
# Support request message file urls
support_request_message_file_router = NestedDefaultRouter(
    support_request_message_router, r"message", lookup="support_request_message"
)
support_request_message_file_router.register(
    r"file", views.SupportRequestMessageFileViewSet, basename="file"
)


urlpatterns = [
    path("", include(router.urls)),
    path("", include(support_request_message_router.urls)),
    path("", include(support_request_message_file_router.urls)),
]
