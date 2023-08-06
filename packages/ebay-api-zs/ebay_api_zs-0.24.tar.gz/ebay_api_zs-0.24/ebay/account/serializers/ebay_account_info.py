from ebay.account import models

# from ebay.order.serializers.api.base import AmountSerializer
from rest_framework import serializers


# class SellingLimitAmountSerializer(AmountSerializer):
#     class Meta:
#         fields = ['value', 'currency']
#
#
# class SellingLimitSerializer(serializers.Serializer):
#     amount = SellingLimitAmountSerializer()
#     quantity = serializers.IntegerField(required=False)
#
#     class Meta:
#         fields = ['amount', 'quantity']
#
#
# class EbayUserAccountPrivilegesSerializer(serializers.ModelSerializer):
#     sellingLimit = SellingLimitSerializer(required=False)
#     sellerRegistrationCompleted = serializers.BooleanField(required=False)

#     def create(self, validated_data):
#         account_info = models.EbayUserAccountInfo.objects.get(
#             ebay_account__marketplace_user_account=validated_data['marketplace_user_account'],
#         )

#         value = validated_data['sellingLimit']['amount']['value']
#         currency = validated_data['sellingLimit']['amount']['currency']
#         quantity = validated_data['sellingLimit']['quantity']
#         sellerRegistrationCompleted = validated_data['sellerRegistrationCompleted']
#
#         obj, created = models.EbayUserAccountPrivileges.objects.update_or_create(
#             account_info=account_info,
#             defaults={
#                 'value': value,
#                 'currency': currency,
#                 'quantity': quantity,
#                 'sellerRegistrationCompleted': sellerRegistrationCompleted,
#             }
#         )
#         return obj
#
#     def update(self, instance, validated_data):
#         return self.create(validated_data=validated_data)
#
#     class Meta:
#         model = models.EbayUserAccountPrivileges
#         fields = ['sellingLimit', 'sellerRegistrationCompleted']
#
#

# Rate limits
# --------------------------------------------


class EbayRateLimitsResourceRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EbayRateLimitsResourceRate
        exclude = ["resource"]


class EbayRateLimitsResourceSerializer(serializers.ModelSerializer):
    rates = EbayRateLimitsResourceRateSerializer(required=False, many=True)

    class Meta:
        model = models.EbayRateLimitsResource
        exclude = ["rate_limits"]


class EbayAppAccountRateLimitsSerializer(serializers.ModelSerializer):
    resources = EbayRateLimitsResourceSerializer(required=False, many=True)

    class Meta:
        model = models.EbayAppRateLimits
        exclude = []

    def create(self, validated_data):
        rate_limits, created = models.EbayAppRateLimits.objects.update_or_create(
            ebay_app_account=validated_data["ebay_app_account"],
            apiContext=validated_data["apiContext"],
            apiName=validated_data["apiName"],
            defaults={"apiVersion": validated_data["apiVersion"],},
        )
        for resource_data in validated_data.pop("resources"):
            resource, created = models.EbayRateLimitsResource.objects.update_or_create(
                rate_limits=rate_limits, name=resource_data["name"],
            )
            for rate_data in resource_data.pop("rates", []):
                models.EbayRateLimitsResourceRate.objects.update_or_create(
                    resource=resource,
                    defaults={
                        "limit": rate_data["limit"],
                        "remaining": rate_data.get("remaining", None),
                        "reset": rate_data.get("reset", None),
                        "timeWindow": rate_data.get("timeWindow", None),
                    },
                )
        return rate_limits
