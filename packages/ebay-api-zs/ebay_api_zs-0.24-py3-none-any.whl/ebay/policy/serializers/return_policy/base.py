from ebay.policy import models
from ebay.policy.serializers import (
    AbstractCategoryTypeSerializer,
    AbstractPolicySerializer,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class ReturnsAcceptedValidationMixin:
    def validate(self, attrs):
        error_dict = dict()
        if attrs.get("returnsAccepted"):
            if not attrs.get("returnShippingCostPayer"):
                error_dict[
                    "returnShippingCostPayer"
                ] = "required if returnsAccepted is set to true."
            if not attrs.get("returnPeriod"):
                error_dict[
                    "returnPeriod"
                ] = "required if returnsAccepted is set to true."
        if error_dict:
            raise ValidationError(error_dict)
        return attrs


class ReturnPolicyReturnPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReturnPolicyReturnPeriod
        exclude = ["id", "return_policy"]


class BaseInternationalOverrideReturnPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.InternationalOverrideReturnPeriod
        exclude = ["id", "international_override"]


class BaseInternationalOverrideSerializer(
    ReturnsAcceptedValidationMixin, serializers.ModelSerializer
):
    returnPeriod = BaseInternationalOverrideReturnPeriodSerializer(required=False)

    class Meta:
        model = models.InternationalOverride
        exclude = ["id", "return_policy"]


class BaseReturnPolicyCategoryTypeSerializer(AbstractCategoryTypeSerializer):
    class Meta(AbstractCategoryTypeSerializer.Meta):
        model = models.ReturnPolicyCategoryType


class BaseReturnPolicySerializer(
    ReturnsAcceptedValidationMixin, AbstractPolicySerializer
):
    categoryTypes = BaseReturnPolicyCategoryTypeSerializer(
        many=True, allow_empty=False, required=False
    )
    internationalOverride = BaseInternationalOverrideSerializer(required=False)
    returnPeriod = ReturnPolicyReturnPeriodSerializer(required=False)

    class Meta(AbstractPolicySerializer.Meta):
        model = models.ReturnPolicy
        fields = AbstractPolicySerializer.Meta.fields + [
            "returnMethod",
            "returnsAccepted",
            "returnShippingCostPayer",
            "internationalOverride",
            "returnPeriod",
        ]
        read_only_fields = AbstractPolicySerializer.Meta.read_only_fields + [
            "returnMethod"
        ]
