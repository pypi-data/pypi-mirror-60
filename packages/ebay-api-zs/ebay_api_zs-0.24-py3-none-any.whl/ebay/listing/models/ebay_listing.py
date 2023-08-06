from django.db import models

from ebay.category.models import EbayCategory
from ebay.data import enums
from ebay.data.marketplace import MarketplaceToLocale
from ebay.location.models import EbayLocation
from ebay.models import AbstractNonConvertedAmount
from ebay.policy.models import FulfillmentPolicy, PaymentPolicy, ReturnPolicy
from model_utils import FieldTracker

from zonesmart.marketplace.models import Channel, MarketplaceEntity
from zonesmart.models import NestedUpdateOrCreateModelManager
from zonesmart.product.models import BaseProduct
from zonesmart.utils.logger import get_logger

logger = get_logger(app_name=__file__)


class EbayListingManager(NestedUpdateOrCreateModelManager):
    RELATED_OBJECT_NAMES = ["aspects", "products", "compatibilities"]
    UPDATE_OR_CREATE_FILTER_FIELDS = {
        "products": ["sku", "offerId"],
        "aspects": ["name"],
    }
    RECREATE_OBJECT_NAMES = ["compatibilities"]


class EbayListing(MarketplaceEntity):
    REQUIRED_FOR_PUBLISHING_FIELDS = (
        MarketplaceEntity.REQUIRED_FOR_PUBLISHING_FIELDS
        + [
            "location",
            "category",
            "fulfillmentPolicy",
            "paymentPolicy",
            "returnPolicy",
        ]
    )
    # Tracker should be added for each model that requires fields update tracking
    # https://github.com/jazzband/django-model-utils/issues/155
    tracker = FieldTracker()
    TRACKER_EXCLUDE_FIELDS = MarketplaceEntity.TRACKER_EXCLUDE_FIELDS + [
        "groupListingId"
    ]
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        limit_choices_to={"domain__marketplace__unique_name": "ebay"},
        related_name="ebay_products",
        related_query_name="ebay_product",
        verbose_name="Пользовательский канал продаж",
    )
    base_product = models.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="ebay_products",
        related_query_name="ebay_product",
        verbose_name="Базовый товар",
    )
    # Fields
    listing_sku = models.CharField(max_length=255, verbose_name="SKU листинга")
    groupListingId = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="ID вариативного листинга",
    )
    title = models.CharField(max_length=255, verbose_name="Наименование")
    # General
    listing_description = models.TextField(
        max_length=500000, blank=True, null=True, verbose_name="Описание для листинга"
    )
    location = models.ForeignKey(
        EbayLocation,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Идентификатор склада для eBay",
    )
    category = models.ForeignKey(
        EbayCategory,
        on_delete=models.CASCADE,
        limit_choices_to={"is_leaf": True},
        related_name="ebay_products",
        related_query_name="ebay_product",
        verbose_name="Категория товара eBay",
    )
    localizedFor = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        choices=enums.LanguageCodeEnum,
        verbose_name="Локализация",
    )
    # Policies
    fulfillmentPolicy = models.ForeignKey(
        FulfillmentPolicy,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"channel__domain__marketplace__unique_name": "ebay"},
        related_name="products",
        related_query_name="product",
        verbose_name="ID политики фулфилмента",
    )
    paymentPolicy = models.ForeignKey(
        PaymentPolicy,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"channel__domain__marketplace__unique_name": "ebay"},
        related_name="products",
        related_query_name="product",
        verbose_name="ID политики оплаты",
    )
    returnPolicy = models.ForeignKey(
        ReturnPolicy,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"channel__domain__marketplace__unique_name": "ebay"},
        related_name="products",
        related_query_name="product",
        verbose_name="ID политики возврата",
    )
    # Best Offer
    bestOfferEnabled = models.BooleanField(
        blank=True, default=False, verbose_name="BestOffer enabled",
    )

    objects = EbayListingManager()

    class Meta:
        verbose_name = "Листинг"
        verbose_name_plural = "Листинги"

    def save(self, *args, **kwargs):
        if not self.localizedFor:
            domain_code = self.channel.domain.code
            try:
                self.localizedFor = MarketplaceToLocale[domain_code]
            except KeyError:
                logger.warning(
                    f"Не удалось установить язык для маркетплейса ({domain_code})"
                )
                self.localizedFor = MarketplaceToLocale["default"]
                logger.debug(f"Установлен язык по умолчанию ({self.localizedFor})")

        super(EbayListing, self).save(*args, **kwargs)

    @property
    def products_num(self):
        if hasattr(self, "products"):
            return self.products.count()
        else:
            return 0

    def _get_products_field(self, field_name: str):
        if self.products_num == 1:
            return getattr(self.products.first(), field_name)
        elif self.products_num > 1:
            return [getattr(product, field_name) for product in self.products.all()]

    @property
    def sku(self):
        return self._get_products_field(field_name="sku")

    @property
    def offerId(self):
        return self._get_products_field(field_name="offerId")

    @property
    def listingId(self):
        return self._get_products_field(field_name="listingId")


class EbayProductAutoAcceptPrice(AbstractNonConvertedAmount):
    ebay_product = models.OneToOneField(
        EbayListing,
        on_delete=models.CASCADE,
        related_name="auto_accepted_price",
        verbose_name="Товар eBay",
    )

    class Meta:
        verbose_name = "Порог цены для автоматического принятия Best Offer"
        verbose_name_plural = verbose_name


class EbayProductAutoDeclinedPrice(AbstractNonConvertedAmount):
    ebay_product = models.OneToOneField(
        EbayListing,
        on_delete=models.CASCADE,
        related_name="auto_declined_price",
        verbose_name="Товар eBay",
    )

    class Meta:
        verbose_name = "Порог цены для автоматического отклонения Best Offer"
        verbose_name_plural = verbose_name
