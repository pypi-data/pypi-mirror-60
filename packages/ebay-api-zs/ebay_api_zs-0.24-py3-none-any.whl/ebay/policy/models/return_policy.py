from django.db import models

from ebay.data import enums
from ebay.policy.models import (
    AbstractCategoryType,
    AbstractPolicy,
    AbstractTimeDuration,
)
from model_utils import Choices, FieldTracker

from zonesmart.marketplace.models import Channel
from zonesmart.models import NestedUpdateOrCreateModelManager, UUIDModel


class ReturnPolicy(AbstractPolicy):
    REQUIRED_FOR_PUBLISHING_FIELDS = AbstractPolicy.REQUIRED_FOR_PUBLISHING_FIELDS + [
        "returnsAccepted"
    ]
    # Tracker should be added for each model that requires fields update tracking
    # https://github.com/jazzband/django-model-utils/issues/155
    tracker = FieldTracker()
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        limit_choices_to={"domain__marketplace__unique_name": "ebay"},
        related_name="return_policies",
        related_query_name="return_policy",
        verbose_name="Аккаунт пользователя eBay",
    )
    # Fields
    returnMethod = models.CharField(
        max_length=11, default="REPLACEMENT", verbose_name="Return method"
    )
    returnsAccepted = models.BooleanField(verbose_name="Returns accepted")
    returnShippingCostPayer = models.CharField(
        max_length=6, blank=True, null=True, choices=enums.ReturnShippingCostPayerEnum,
    )

    objects = NestedUpdateOrCreateModelManager()
    # Deprecated fields
    # Field extendedHolidayReturnsOffered is deprecated as of version 1.2.0, released on May 31, 2018.
    # https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/createReturnPolicy#request.extendedHolidayReturnsOffered  # noqa
    # extendedHolidayReturnsOffered = models.BooleanField(
    #     blank=True, null=True, editable=False,
    #     verbose_name='Seller offers Extended Holiday Returns policy',
    # )
    # Field refundMethod is deprecated as of version 1.2.0, released on May 31, 2018.
    # https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/createReturnPolicy#request.refundMethod  # noqa
    # refundMethod = models.CharField(
    #     max_length=18, blank=True, null=True, editable=False,
    #     choices=enums.RefundMethodEnum,
    #     verbose_name='Refund method'
    # )
    # Field restockingFeePercentage is deprecated as of version 1.2.0, released on May 31, 2018.
    # https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/createReturnPolicy#request.restockingFeePercentage  # noqa
    # restockingFeePercentage = models.FloatField(
    #     blank=True, null=True, editable=False,
    #     verbose_name='Restocking fee percentage'
    # )
    # Field returnInstructions is deprecated as of version 1.2.0, released on May 31, 2018.
    # https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/createReturnPolicy#request.returnInstructions  # noqa
    # returnInstructions = models.CharField(
    #     max_length=8000, blank=True, null=True, editable=False,
    #     verbose_name='Return instructions'
    # )

    class Meta:
        verbose_name = "Политика возврата"
        verbose_name_plural = "Политики возврата"
        default_related_name = "return_policy"


class ReturnPolicyCategoryType(AbstractCategoryType):
    return_policy = models.ForeignKey(
        ReturnPolicy,
        on_delete=models.CASCADE,
        related_name="categoryTypes",
        verbose_name="Return policy",
    )
    # Overridden field from CategoryType
    # Default CategoryType (for return policies only)
    # Note for return policies: The 'MOTORS_VEHICLES' category type
    # is not valid for return policies because eBay flows do not support
    # the return of motor vehicles.
    # https://developer.ebay.com/api-docs/sell/account/resources/return_policy/methods/createReturnPolicy#request.categoryTypes  # noqa
    name = models.CharField(
        max_length=29,
        editable=False,
        default=enums.CategoryTypeEnum.ALL_EXCLUDING_MOTORS_VEHICLES,
        verbose_name="Name",
    )


class InternationalOverride(UUIDModel):
    return_policy = models.OneToOneField(
        ReturnPolicy,
        on_delete=models.CASCADE,
        related_name="internationalOverride",
        verbose_name="Return policy",
    )
    # Fields
    returnMethod = models.CharField(
        max_length=30, default="REPLACEMENT", verbose_name="Return method"
    )
    returnsAccepted = models.BooleanField(
        blank=True, null=True, verbose_name="Seller allows international returns"
    )
    returnShippingCostPayer = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        choices=enums.ReturnShippingCostPayerEnum,
        verbose_name="Return shipping cost payer",
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Seller's policy for international returns"
        verbose_name_plural = "Seller's policies for international returns"


class InternationalOverrideReturnPeriod(AbstractTimeDuration):
    international_override = models.OneToOneField(
        InternationalOverride,
        on_delete=models.CASCADE,
        related_name="returnPeriod",
        verbose_name="International return override type",
    )

    class Meta:
        verbose_name = "Amount of time the buyer has to return an item"
        verbose_name_plural = "Amounts of times the buyer has to return an item"


class ReturnPolicyReturnPeriod(AbstractTimeDuration):
    VALUE_CHOICES = Choices((30, "thirty", "30"), (60, "sixty", "60"),)
    return_policy = models.OneToOneField(
        ReturnPolicy,
        on_delete=models.CASCADE,
        related_name="returnPeriod",
        verbose_name="Return policy",
    )
    # Fields
    unit = models.CharField(
        max_length=100,
        editable=False,
        default=enums.TimeDurationUnitEnum.DAY,
        verbose_name="Unit",
    )
    value = models.PositiveIntegerField(choices=VALUE_CHOICES, verbose_name="Value")

    class Meta:
        verbose_name = "Amount of time the buyer has to return an item"
        verbose_name_plural = "Amounts of times the buyer has to return an item"
