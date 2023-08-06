from amazon.order.actions import DownloadAmazonOrders
from amazon.order.serializers.order import (
    BaseAmazonOrderSerializer,
    CreateAmazonOrderSerializer,
)
from rest_framework import mixins

from zonesmart import remote_action_views
from zonesmart.views import GenericSerializerViewSet


class AmazonOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    remote_action_views.RemoteDownloadListActionByChannel,
    GenericSerializerViewSet,
):
    remote_api_actions = {"remote_download_list": DownloadAmazonOrders}
    serializer_classes = {
        "default": BaseAmazonOrderSerializer,
        "create": CreateAmazonOrderSerializer,
    }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                channel__marketplace_user_account__in=self.request.user.marketplace_accounts.all()
            )
        )
