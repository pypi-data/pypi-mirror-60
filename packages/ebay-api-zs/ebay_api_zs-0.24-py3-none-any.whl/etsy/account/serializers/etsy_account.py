from django.utils import timezone

from etsy.account.models import EtsyUserAccount, EtsyUserAccountInfo
from rest_framework import serializers

from etsy.account.serializers.bill import (
    EtsyUserBillingOverviewSerializer,
    EtsyBillChargeSerializer,
)
from zonesmart.marketplace.serializers.marketplace_user_account import (
    MarketplaceUserAccountSerializer,
)


class CreateEtsyUserAccountSerializer(serializers.ModelSerializer):
    oauth_token = serializers.CharField()
    oauth_verifier = serializers.CharField()

    class Meta:
        model = EtsyUserAccount
        fields = [
            "oauth_token",
            "oauth_verifier",
        ]


class FeedbackInfoSerializer(serializers.Serializer):
    count = serializers.IntegerField(source="feedback_count")
    score = serializers.IntegerField(source="feedback_score", allow_null=True)


class EtsyUserAccountInfoSerializer(serializers.ModelSerializer):
    feedback_info = FeedbackInfoSerializer(source="*")

    class Meta:
        model = EtsyUserAccountInfo
        exclude = ["etsy_account"]


class DownloadEtsyUserAccountInfoSerializer(EtsyUserAccountInfoSerializer):
    feedback_info = FeedbackInfoSerializer()

    class Meta(EtsyUserAccountInfoSerializer.Meta):
        pass

    def to_internal_value(self, data):
        creation_tsz = data.pop("creation_tsz")
        if creation_tsz:
            data["creation_tsz"] = timezone.make_aware(
                timezone.datetime.fromtimestamp(creation_tsz)
            )
        return super().to_internal_value(data)

    def create(self, validated_data):
        feedback_info = validated_data.pop("feedback_info")
        return super().create(validated_data={**validated_data, **feedback_info})


class EtsyUserAccountSerializer(serializers.ModelSerializer):
    marketplace_user_account = MarketplaceUserAccountSerializer(read_only=True)
    user_info = EtsyUserAccountInfoSerializer()
    billing_overview = EtsyUserBillingOverviewSerializer()
    bill_charges = EtsyBillChargeSerializer(many=True)

    class Meta:
        model = EtsyUserAccount
        fields = "__all__"
