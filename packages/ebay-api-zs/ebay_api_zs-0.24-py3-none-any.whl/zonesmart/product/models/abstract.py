from django.db import models

from ebay.data.marketplace import MarketplaceToCurrency

from zonesmart.data.enums import CurrencyCodeEnum
from zonesmart.marketplace.models import MarketplaceEntity
from zonesmart.product.models import ProductCodeType, ProductImage
from zonesmart.utils import converter, logger

logger = logger.get_logger(app_name=__file__)


class AbstractPrice(models.Model):
    value = models.FloatField(verbose_name="Цена")
    currency = models.CharField(
        max_length=20, choices=CurrencyCodeEnum, verbose_name="Валюта"
    )
    converted_from_value = models.FloatField(
        blank=True, null=True, verbose_name="Исходная цена"
    )
    converted_from_currency = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=CurrencyCodeEnum,
        verbose_name="Исходная валюта",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.value} {self.currency}"

    def convert_price(self, domain):  # отрефакторить
        self.converted_from_currency = self.currency
        try:
            self.currency = MarketplaceToCurrency[domain]
        except KeyError:
            logger.warning(f"Не удалось установить валюту для маркетплейса ({domain})")
            self.currency = MarketplaceToCurrency["default"]
            logger.debug(f"Установлена валюта по умолчанию ({self.currency})")
        if self.currency != self.converted_from_currency:
            self.converted_from_value = self.value
            self.value = converter.convert_amount(
                from_currency=self.converted_from_currency,
                to_currency=self.currency,
                value=self.value,
            )
        return self.value


class AbstractProduct(AbstractPrice):
    EXTRA_IMAGES_LIMIT = 5
    sku = models.CharField(max_length=50, verbose_name="SKU")
    description = models.TextField(max_length=500000, verbose_name="Описание продукта")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество",)
    main_image = models.ForeignKey(
        ProductImage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(class)s_main_images",
        related_query_name="%(class)s_main_image",
        verbose_name="Главное изображение",
    )
    extra_images = models.ManyToManyField(
        ProductImage,
        blank=True,
        related_name="%(class)s_extras",
        related_query_name="%(class)s_extra",
        verbose_name="Дополнительные изображения",
    )
    product_id_code_type = models.ForeignKey(
        ProductCodeType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Тип кода товара",
    )
    product_id_code = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Код товара"
    )

    class Meta:
        abstract = True
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.sku


class AbstractMarketplaceProduct(AbstractProduct, MarketplaceEntity):
    REQUIRED_FOR_PUBLISHING_FIELDS = [
        "sku",
        "title",
        "description",
        "value",
        "currency",
        "main_image",
    ]

    class Meta:
        abstract = True
