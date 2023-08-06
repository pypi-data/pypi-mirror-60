from ebay.policy.actions import RemoteDownloadReturnPolicyList
from ebay.policy.actions.return_policy import (
    UpdateReturnPolicy,
    UploadReturnPolicy,
    WithdrawReturnPolicy,
)
from ebay.policy.filters import ReturnPolicyFilterSet
from ebay.policy.serializers.return_policy import (
    BaseReturnPolicySerializer,
    CreateReturnPolicySerializer,
    UpdateReturnPolicySerializer,
)
from ebay.policy.views import PolicyViewSet


class ReturnPolicyViewSet(PolicyViewSet):
    """
    ViewSet for return policy model
    """

    remote_api_actions = {
        "remote_download_list": RemoteDownloadReturnPolicyList,
        "remote_create": UploadReturnPolicy,
        "remote_delete": WithdrawReturnPolicy,
        "remote_update": UpdateReturnPolicy,
    }
    serializer_classes = {
        "default": BaseReturnPolicySerializer,
        "create": CreateReturnPolicySerializer,
        "update": UpdateReturnPolicySerializer,
        "partial_update": UpdateReturnPolicySerializer,
    }
    filterset_class = ReturnPolicyFilterSet
