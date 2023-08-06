from django.db import models

from ebay.data import enums
from ebay.models.abstract import AbstractAmount
from ebay.order.models import EbayOrder


class PaymentSummary(models.Model):
    order = models.OneToOneField(
        EbayOrder, on_delete=models.CASCADE, related_name="payment_summary"
    )
    # Fields
    shippingServiceCode = models.CharField(
        max_length=100, verbose_name="ID службы доставки"
    )


class Payment(models.Model):
    payment_summary = models.ForeignKey(
        PaymentSummary,
        on_delete=models.CASCADE,
        related_name="payments",
        related_query_name="payment",
    )
    # Fields
    paymentDate = models.DateTimeField(blank=True, null=True)
    paymentMethod = models.CharField(max_length=30, choices=enums.PaymentMethodTypeEnum)
    paymentReferenceId = models.CharField(max_length=255, blank=True, null=True)
    paymentStatus = models.CharField(max_length=30, choices=enums.PaymentStatusEnum)


class PaymentAmount(AbstractAmount):
    payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, related_name="amount"
    )


class PaymentHold(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="payment_holds",
        related_query_name="payment_hold",
    )
    # Fields
    expectedReleaseDate = models.DateTimeField(blank=True, null=True)
    holdReason = models.CharField(max_length=255, blank=True, null=True)
    holdState = models.CharField(
        max_length=30, blank=True, null=True, choices=enums.PaymentHoldStateEnum
    )
    releaseDate = models.DateTimeField(blank=True, null=True)


class HoldAmount(AbstractAmount):
    payment_hold = models.OneToOneField(
        PaymentHold, on_delete=models.CASCADE, related_name="amount"
    )


class SellerActionsToRelease(models.Model):
    payment_hold = models.ForeignKey(
        PaymentHold,
        on_delete=models.CASCADE,
        related_name="seller_actions_to_release",
        related_query_name="seller_action_to_release",
    )
    # Fields
    sellerActionToRelease = models.CharField(max_length=255, blank=True, null=True)


class OrderRefund(models.Model):
    payment_summary = models.ForeignKey(
        PaymentSummary,
        on_delete=models.CASCADE,
        related_name="refunds",
        related_query_name="refund",
    )
    # Fields
    refundDate = models.DateTimeField(blank=True, null=True)
    refundId = models.CharField(max_length=255, blank=True, null=True)
    refundReferenceId = models.CharField(max_length=100, blank=True, null=True)
    refundStatus = models.CharField(
        max_length=30, blank=True, null=True, choices=enums.RefundStatusEnum
    )


class OrderRefundAmount(AbstractAmount):
    order_refund = models.OneToOneField(
        OrderRefund, on_delete=models.CASCADE, related_name="amount"
    )


class TotalDueSeller(AbstractAmount):
    payment_summary = models.OneToOneField(
        PaymentSummary, on_delete=models.CASCADE, related_name="total_due_seller"
    )
