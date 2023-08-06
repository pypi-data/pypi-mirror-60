from ebay.policy.serializers.payment_policy import BasePaymentPolicySerializer


class RemoteDownloadPaymentPolicySerializer(BasePaymentPolicySerializer):
    class Meta(BasePaymentPolicySerializer.Meta):
        read_only_fields = ["id"]
