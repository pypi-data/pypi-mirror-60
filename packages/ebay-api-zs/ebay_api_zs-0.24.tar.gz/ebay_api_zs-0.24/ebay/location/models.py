import uuid

from django.db import models

from ebay.data import enums
from ebay.models import AbstractAddress
from model_utils import FieldTracker
from multiselectfield import MultiSelectField

from zonesmart.marketplace.models import MarketplaceEntity, MarketplaceUserAccount


class EbayLocation(AbstractAddress, MarketplaceEntity):
    # Tracker should be added for each model that requires fields update tracking
    # https://github.com/jazzband/django-model-utils/issues/155
    tracker = FieldTracker()
    name = models.CharField(max_length=1000, verbose_name="Название")
    marketplace_user_account = models.ForeignKey(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        related_name="ebay_locations",
        related_query_name="ebay_location",
        verbose_name="Пользовательский аккаунт маркетплейса",
    )
    merchantLocationKey = models.CharField(
        max_length=36, default=uuid.uuid4, verbose_name="ID склада"
    )
    # UTC
    utcOffsetChoices = [(f"{i}:00", f"{i}:00") for i in range(-12, 13)]
    utcOffset = models.CharField(
        max_length=6, default="0", choices=utcOffsetChoices, verbose_name="Часовой пояс"
    )
    # GeoCoordinates
    latitude = models.FloatField(  # Point instead of FloatField
        blank=True, null=True, verbose_name="Широта"
    )
    longitude = models.FloatField(blank=True, null=True, verbose_name="Долгота")
    locationAdditionalInformation = models.TextField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Дополнительная информация об адресе",
    )
    locationInstructions = models.TextField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Инструкции по местоположению",
    )
    locationWebUrl = models.URLField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name="URL, ассоциированный с местоположением",
    )
    phone = models.CharField(
        max_length=36, blank=True, null=True, verbose_name="Телефонный номер владельца"
    )
    locationTypes = MultiSelectField(
        max_length=20,
        default=[enums.LocationTypeEnum.WAREHOUSE],
        choices=enums.LocationTypeEnum,
        verbose_name="Тип склада",
    )
    # Managing by enable/disable InventoryLocation request
    merchantLocationStatus = models.CharField(
        max_length=20,
        blank=True,
        default=enums.StatusEnum.ENABLED,
        choices=enums.StatusEnum,
        verbose_name="Статус мерчанта",
    )

    class Meta:
        verbose_name = "Склад для eBay"
        verbose_name_plural = "Склады для eBay"
        constraints = [
            models.UniqueConstraint(
                fields=["marketplace_user_account", "merchantLocationKey"],
                name="unique_marketplace_user_account",
            )
        ]

    def __str__(self):
        return self.name
