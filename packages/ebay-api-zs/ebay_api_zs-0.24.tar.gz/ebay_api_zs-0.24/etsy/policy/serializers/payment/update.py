from etsy.policy.serializers.payment.base import BaseEtsyPaymentTemplateSerializer


class UpdateEtsyPaymentTemplateSerializer(BaseEtsyPaymentTemplateSerializer):
    class Meta(BaseEtsyPaymentTemplateSerializer.Meta):
        fields = [
            "allow_check",
            "allow_mo",
            "allow_other",
            "allow_paypal",
            "allow_cc",
            "paypal_email",
            "name",
            "first_line",
            "second_line",
            "city",
            "state",
            "zip",
            "country",
        ]
