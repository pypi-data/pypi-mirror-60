from rest_framework.decorators import action

from ebay.account.actions import RemoteDownloadEbayUserAccountInfo
from ebay.account.models import EbayUserAccount
from ebay.account.serializers.ebay_user_account import (
    CreateEbayUserAccountSerializer,
    EbayUserAccountSerializer,
)
from ebay.account.serializers.profile.base import EbayUserAccountProfileSerializer
from ebay.account.serializers.validators import EbayUserAccountValidator
from ebay.api.ebay_access import EbayAPIAccess
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from zonesmart.marketplace.models import MarketplaceUserAccount, Marketplace
from zonesmart.views import GenericSerializerViewSet
from zonesmart.remote_action_views import RemoteActionResponseViewSet


class EbayUserAccountViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    RemoteActionResponseViewSet,
    GenericSerializerViewSet,
):
    remote_api_actions = {"remote_sync": RemoteDownloadEbayUserAccountInfo}
    serializer_classes = {
        "default": EbayUserAccountSerializer,
        "create": CreateEbayUserAccountSerializer,
    }

    def get_queryset(self):
        return (
            super()
            .get_serializer_class()
            .Meta.model.objects.filter(marketplace_user_account__user=self.request.user)
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Validate ebay user account (is active or not) and also return token data,
        # user data & privileges data
        validator = EbayUserAccountValidator(
            code=serializer.validated_data["code"], user=self.request.user
        )
        validator.is_valid()
        results = validator.get_results()
        # Create basic profile serializer kwargs
        profile_kwargs = {"data": results["user"]}
        # Check if EbayUserAccountProfile with returned user_id already exits
        # and creates first MarketplaceUserAccount & EbayUserAccount if it's not
        if validator.profile:
            ebay_user_account = validator.profile.ebay_user_account
            EbayUserAccount.objects.filter(id=ebay_user_account.id).update(
                **validator.token_data, sandbox=validator.is_sandbox
            )
        else:
            # Create MarketplaceUserAccount
            marketplace_user_account = MarketplaceUserAccount.objects.create(
                user=self.request.user,
                marketplace=Marketplace.objects.get(unique_name="ebay"),
            )
            # Create EbayUserAccount
            ebay_user_account = EbayUserAccount.objects.create(
                **validator.token_data,
                marketplace_user_account=marketplace_user_account,
                sandbox=validator.is_sandbox,
            )
        # Create or update EbayUserAccountProfile
        profile_serializer = EbayUserAccountProfileSerializer(**profile_kwargs)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save(ebay_user_account=ebay_user_account)
        # Get success headers & data, then return response
        headers = self.get_success_headers(serializer.data)
        data = EbayUserAccountSerializer().to_representation(ebay_user_account)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["POST"])
    def remote_sync(self, request, *args, **kwargs) -> Response:
        account = self.get_object()
        action_init_kwargs = {
            "marketplace_user_account_id": account.marketplace_user_account_id
        }
        return self.get_action_response(
            required_statuses=["update_required", "ready_to_publish"],
            action_init_kwargs=action_init_kwargs,
        )


class EbayUserAccountAuthUrl(APIView):
    def get(self, request, *args, **kwargs):
        api = EbayAPIAccess()
        return Response(api.get_auth_url())
