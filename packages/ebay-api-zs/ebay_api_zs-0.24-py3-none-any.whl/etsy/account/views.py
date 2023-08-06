from django.core.cache import cache

from etsy.account.actions.etsy_account import CreateOrUpdateEtsyUserAccount
from etsy.account.actions.billing import (
    RemoteDownloadUserBillingOverview,
    RemoteDownloadUserBillChargeList,
)
from etsy.account.actions.etsy_account import DownloadEtsyUserAccountInfo
from etsy.account.serializers import (
    CreateEtsyUserAccountSerializer,
    EtsyUserAccountSerializer,
)
from etsy.api.etsy_access import EtsyAPIAccess, EtsyAPIAccessError
from etsy.account.actions import RemoteDownloadEtsyShopsAndSections
from etsy.policy.actions import RemoteDownloadEtsyPaymentTemplateList

from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from zonesmart.views import GenericSerializerViewSet


class EtsyUserAccountViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericSerializerViewSet,
):
    serializer_classes = {
        "default": EtsyUserAccountSerializer,
        "create": CreateEtsyUserAccountSerializer,
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

        oauth_verifier = serializer.validated_data["oauth_verifier"]
        temp_access_token = serializer.validated_data["oauth_token"]
        # Get secret token key from cache
        temp_access_token_secret = cache.get(temp_access_token)
        cache.expire(temp_access_token, timeout=0)
        # print(temp_access_token, "\n", temp_access_token_secret)
        try:
            # get token and create or update user account with dependencies
            is_success, message, objects = CreateOrUpdateEtsyUserAccount(
                raise_exception=True
            )(
                oauth_verifier=oauth_verifier,
                temp_access_token=temp_access_token,
                temp_access_token_secret=temp_access_token_secret,
            )

            # Download PaymentTemplate
            RemoteDownloadEtsyPaymentTemplateList(
                channel=objects["results"]["channel"], raise_exception=True,
            )()

            marketplace_user_account = (objects["results"]["marketplace_user_account"],)

            # Download user shops and shop sections
            RemoteDownloadEtsyShopsAndSections(
                marketplace_user_account=marketplace_user_account, raise_exception=True,
            )()

            # Download profile
            DownloadEtsyUserAccountInfo(
                marketplace_user_account=marketplace_user_account, raise_exception=True,
            )()

            # Download bill overview
            RemoteDownloadUserBillingOverview(
                marketplace_user_account=marketplace_user_account, raise_exception=True,
            )()

            # Download bill charges
            RemoteDownloadUserBillChargeList(
                marketplace_user_account=marketplace_user_account, raise_exception=True,
            )()

        except EtsyAPIAccess.exception_class as error:
            message = f"Не удалось создать аккаунт Etsy.\n{error}"
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class EtsyUserAccountAuthUrl(APIView):
    def get(self, request, *args, **kwargs):
        api = EtsyAPIAccess()
        try:
            temp_token = api.get_temp_token()
        except EtsyAPIAccessError as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        # print(temp_token)
        temp_access_token = temp_token.key
        temp_access_token_secret = temp_token.secret
        # save secret token key in cache
        cache.set(temp_access_token, temp_access_token_secret, timeout=600)

        url = api.get_auth_url(temp_access_token=temp_access_token)
        return Response(url)
