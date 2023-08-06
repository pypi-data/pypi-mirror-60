from ebay.negotiation.actions import (
    GetEbayMessageList,
    MarkEbayMessageRead,
    ReplyEbayMessage,
)
from ebay.negotiation.models import EbayMessage
from ebay.negotiation.serializers.message import BaseEbayMessageSerializer
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from zonesmart.remote_action_views import (
    RemoteActionResponseViewSet,
    RemoteDownloadListActionByMarketplaceAccount,
)
from zonesmart.views import GenericSerializerViewSet


class RemoteEbayMessageReplyAction(RemoteActionResponseViewSet):
    @action(detail=True, methods=["POST"])
    def remote_reply(self, request: Request, *args, **kwargs) -> Response:
        # Check if request contains a message_body
        message_body = request.data.get("message_body")
        if message_body is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "message_body is missing in request body."},
            )
        # Get message and create initial kwargs for action & call
        message: EbayMessage = self.get_object()
        action_init_kwargs = {
            "marketplace_user_account_id": message.marketplace_user_account.id
        }
        action_call_kwargs = {
            "message_id": message.message_id,
            "message_body": request.data.get("message_body"),
        }
        return self.get_action_response(
            detail=False,
            action_init_kwargs=action_init_kwargs,
            action_call_kwargs=action_call_kwargs,
        )


class RemoteEbayMessageMarkAsReadAction(RemoteActionResponseViewSet):
    @action(detail=True, methods=["POST"])
    def remote_mark_as_read(self, request, *args, **kwargs) -> Response:
        message: EbayMessage = self.get_object()
        return self.get_action_response(
            ignore_status=True,
            action_init_kwargs={
                "marketplace_user_account": message.marketplace_user_account
            },
            action_call_kwargs={"message_id": message.message_id},
        )


class EbayMessageViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    RemoteDownloadListActionByMarketplaceAccount,
    RemoteEbayMessageReplyAction,
    RemoteEbayMessageMarkAsReadAction,
    GenericSerializerViewSet,
):
    lookup_field = "message_id"
    serializer_classes = {"default": BaseEbayMessageSerializer}
    remote_api_actions = {
        "remote_download_list": GetEbayMessageList,
        "remote_reply": ReplyEbayMessage,
        "remote_mark_as_read": MarkEbayMessageRead,
    }
