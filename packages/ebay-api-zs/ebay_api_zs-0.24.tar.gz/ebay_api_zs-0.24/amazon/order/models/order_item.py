# docs: http://docs.developer.amazonservices.com/en_IN/orders-2013-09-01/Orders_Datatypes.html#Order

from django.db import models

from amazon.order.models import AmazonOrder

from zonesmart.models import UUIDModel


class Money(models.Model):
    CurrencyCode = models.CharField(max_length=3)
    Amount = models.FloatField()

    class Meta:
        abstract = True


class AmazonOrderItem(UUIDModel):
    order = models.ForeignKey(
        AmazonOrder, on_delete=models.CASCADE, related_name="order_items"
    )
    ASIN = models.CharField(max_length=30)
    OrderItemId = models.CharField(max_length=30)
    SellerSKU = models.CharField(max_length=100, blank=True, null=True)
    Title = models.CharField(max_length=255, blank=True, null=True)
    QuantityOrdered = models.PositiveSmallIntegerField()
    QuantityShipped = models.PositiveSmallIntegerField()
    # PromotionIds = models.CharField(max_length=50, blank=True, null=True)
    IsGift = models.BooleanField(blank=True, null=True)
    GiftMessageText = models.CharField(max_length=300, blank=True, null=True)
    GiftWrapLevel = models.CharField(max_length=50, blank=True, null=True)
    ConditionNote = models.CharField(max_length=300, blank=True, null=True)
    ConditionId = models.CharField(max_length=30, blank=True, null=True)
    ConditionSubtypeId = models.CharField(max_length=30, blank=True, null=True)
    IsTransparency = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"Товар из заказа Amazon (ID: {self.OrderItemId})"

    class Meta:
        verbose_name = "Товар из заказа Amazon"
        verbose_name_plural = "Товары из заказа Amazon"


class ItemPrice(Money):
    order_item = models.OneToOneField(
        AmazonOrderItem, on_delete=models.CASCADE, related_name="item_price"
    )


class ShippingPrice(Money):
    order_item = models.OneToOneField(
        AmazonOrderItem, on_delete=models.CASCADE, related_name="shipping_price"
    )


class GiftWrapPrice(Money):
    order_item = models.OneToOneField(
        AmazonOrderItem, on_delete=models.CASCADE, related_name="gift_wrap_price"
    )


class ItemTax(Money):
    order_item = models.OneToOneField(
        AmazonOrderItem, on_delete=models.CASCADE, related_name="item_tax"
    )


class ShippingTax(Money):
    order_item = models.OneToOneField(
        AmazonOrderItem, on_delete=models.CASCADE, related_name="shipping_tax"
    )


class GiftWrapTax(Money):
    order_item = models.OneToOneField(
        AmazonOrderItem, on_delete=models.CASCADE, related_name="gift_wrap_tax"
    )


class ShippingDiscount(Money):
    order_item = models.OneToOneField(
        AmazonOrderItem, on_delete=models.CASCADE, related_name="shipping_discount"
    )


class PromotionDiscount(Money):
    order_item = models.OneToOneField(
        AmazonOrderItem, on_delete=models.CASCADE, related_name="promotion_discount"
    )
