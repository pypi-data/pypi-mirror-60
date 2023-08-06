from ebay.account.models import EbayUserAccount
from ebay.account.serializers.profile.base import EbayUserAccountProfileSerializer
from rest_framework import serializers

from zonesmart.marketplace.serializers.marketplace_user_account import (
    MarketplaceUserAccountSerializer,
)


class EbayUserAccountSerializer(serializers.ModelSerializer):
    marketplace_user_account = MarketplaceUserAccountSerializer(read_only=True)
    profile = EbayUserAccountProfileSerializer()

    class Meta:
        model = EbayUserAccount
        fields = "__all__"


class CreateEbayUserAccountSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = EbayUserAccount
        fields = ["code"]
