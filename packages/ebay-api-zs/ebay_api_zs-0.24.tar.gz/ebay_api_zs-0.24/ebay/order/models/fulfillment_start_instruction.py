from django.db import models

from ebay.data import enums
from ebay.models import AbstractAddress


class FulfillmentStartInstruction(models.Model):
    order = models.ForeignKey(
        "EbayOrder",
        on_delete=models.CASCADE,
        related_name="fulfillment_start_instructions",
        related_query_name="fulfillment_start_instruction",
        verbose_name="Заказ",
    )
    # Fields
    destinationTimeZone = models.CharField(max_length=30, blank=True, null=True)
    ebaySupportedFulfillment = models.BooleanField(
        blank=True, null=True, verbose_name="eBay's Global Shipping Program"
    )
    fulfillmentInstructionsType = models.CharField(
        max_length=30,
        choices=enums.FulfillmentInstructionsType,
        verbose_name="Тип метода фулфилмента",
    )
    maxEstimatedDeliveryDate = models.DateTimeField(
        blank=True, null=True, verbose_name="Наиболее поздние дата и время доставки"
    )
    minEstimatedDeliveryDate = models.DateTimeField(
        blank=True, null=True, verbose_name="Наиболее ранние дата и время доставки"
    )
    # PickupStep
    # https://developer.ebay.com/api-docs/sell/fulfillment/types/sel:PickupStep
    merchantLocationKey = models.CharField(
        max_length=36,
        blank=True,
        null=True,
        unique=True,
        verbose_name="ID склада товаров продавца",
    )

    class Meta:
        verbose_name = "Данные о фулфилменте заказа"
        verbose_name_plural = "Данные о фулфилменте заказа"


class FinalDestinationAddress(AbstractAddress):
    fulfillment_start_instruction = models.OneToOneField(
        FulfillmentStartInstruction,
        on_delete=models.CASCADE,
        related_name="final_destination_address",
    )

    class Meta:
        verbose_name = (
            "Конечный адрес назначения для доставки по Глобальной программе доставки"
        )
        verbose_name_plural = (
            "Конечные адреса назначения для доставки по Глобальной программе доставки"
        )


class ShippingStep(models.Model):
    fulfillment_start_instruction = models.OneToOneField(
        FulfillmentStartInstruction,
        on_delete=models.CASCADE,
        related_name="shipping_step",
    )
    # Fields
    shippingCarrierCode = models.CharField(
        max_length=100,
        choices=enums.ShippingCarriersEnum,
        blank=True,
        null=True,
        verbose_name="ID курьерской службы",
    )
    shippingServiceCode = models.CharField(max_length=100)
    shipToReferenceId = models.CharField(max_length=255, blank=True, null=True)


class ShipTo(models.Model):
    shipping_step = models.OneToOneField(
        ShippingStep, on_delete=models.CASCADE, related_name="ship_to"
    )
    # Fields
    companyName = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail покупателя")
    fullName = models.CharField(max_length=100, verbose_name="Полное имя покупателя")
    # PhoneNumber
    # https://developer.ebay.com/api-docs/sell/fulfillment/types/ba:PhoneNumber
    phoneNumber = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Телефонный номер покупателя"
    )


class ContactAddress(AbstractAddress):
    ship_to = models.OneToOneField(
        ShipTo, on_delete=models.CASCADE, related_name="contact_address"
    )
