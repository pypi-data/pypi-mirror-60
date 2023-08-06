from ebay.order.actions import RemoteDownloadEbayOrders
from ebay.order.serializers import BaseEbayOrderSerializer, RetrieveEbayOrderSerializer
from rest_framework import mixins

from zonesmart.remote_action_views import RemoteDownloadListActionByMarketplaceAccount
from zonesmart.views import GenericSerializerViewSet


class EbayOrderViewSet(
    RemoteDownloadListActionByMarketplaceAccount,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericSerializerViewSet,
):
    """
    EbayOrder ViewSet
    """

    remote_api_actions = {"remote_download_list": RemoteDownloadEbayOrders}
    serializer_classes = {
        "default": BaseEbayOrderSerializer,
        "retrieve": RetrieveEbayOrderSerializer,
        "list": RetrieveEbayOrderSerializer,
    }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(marketplace_user_account__user=self.request.user)
        )
