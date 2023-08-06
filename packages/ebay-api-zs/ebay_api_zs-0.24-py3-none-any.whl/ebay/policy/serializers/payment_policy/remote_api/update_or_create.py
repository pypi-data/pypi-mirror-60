from ebay.policy.serializers.payment_policy import BasePaymentPolicySerializer
from rest_framework import serializers

from zonesmart.serializers import NotNullAndEmptyStringModelSerializer


class UpdateOrCreatePaymentPolicySerializer(
    BasePaymentPolicySerializer, NotNullAndEmptyStringModelSerializer
):
    marketplaceId = serializers.CharField(source="channel.domain.code")

    class Meta:
        model = BasePaymentPolicySerializer.Meta.model
        exclude = ["id", "channel", "status", "created", "modified", "published_at"]
