import json

from django.db import models
from model_utils import FieldTracker

from etsy.category.models import EtsyCategory
from etsy.data import enums
from etsy.data.enums import CurrencyCodeEnum
from etsy.account.models.shop import EtsyShopSection
from etsy.policy.models import EtsyShippingTemplate

from zonesmart.marketplace.models import Channel, MarketplaceEntity
from zonesmart.product.models import BaseProduct


from zonesmart.models import NestedUpdateOrCreateModelManager


class EtsyListingManager(NestedUpdateOrCreateModelManager):
    UPDATE_OR_CREATE_FILTER_FIELDS = {"products": ["product_id"]}


class EtsyListing(MarketplaceEntity):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/listing#section_fields
    """

    REQUIRED_FOR_PUBLISHING_FIELDS = (
        MarketplaceEntity.REQUIRED_FOR_PUBLISHING_FIELDS
        + [
            "shipping_template",
            "title",
            "description",
            "min_price",
            "total_quantity",
            "who_made",
            "when_made",
            "is_supply",
        ]
    )
    EXTRA_IMAGES_LIMIT = 10
    # Tracker should be added for each model that requires fields update tracking
    # https://github.com/jazzband/django-model-utils/issues/155
    tracker = FieldTracker()
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        limit_choices_to={"domain__marketplace__unique_name": "etsy"},
        related_name="etsy_products",
        related_query_name="etsy_product",
        verbose_name="Пользовательский канал продаж",
    )
    base_product = models.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="etsy_products",
        related_query_name="etsy_product",
        verbose_name="Базовый листинг",
    )
    # Fields
    listing_id = models.CharField(
        max_length=30, blank=True, null=True, unique=True, verbose_name="ID листинга",
    )
    shop_section = models.ForeignKey(
        EtsyShopSection,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="listings",
        related_query_name="listing",
        verbose_name="Секция магазина Etsy",
    )
    category = models.ForeignKey(
        EtsyCategory,
        on_delete=models.CASCADE,
        limit_choices_to={"is_leaf": True},
        related_name="etsy_products",
        related_query_name="etsy_product",
        verbose_name="Категория листинга Etsy",
    )
    shipping_template = models.ForeignKey(
        EtsyShippingTemplate,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="etsy_products",
        related_query_name="etsy_product",
        verbose_name="Политика доставки",
    )

    creation_tsz = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время создания листинга в системе Etsy",
    )
    ending_tsz = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время завершения листинга в системе Etsy",
    )
    original_creation_tsz = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время публикации листинга в системе Etsy",
    )
    last_modified_tsz = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время последнего обновления листинга в системе Etsy",
    )
    state_tsz = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время последнего обновления статуса листинга в системе Etsy",
    )

    title = models.CharField(max_length=300, verbose_name="Заголовок")
    description = models.TextField(max_length=4000, verbose_name="Описание листинга")
    price = models.FloatField(verbose_name="Минимальная цена (USD)")
    currency_code = models.CharField(
        max_length=3, choices=CurrencyCodeEnum, verbose_name="Валюта"
    )
    total_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Общее количество",
    )
    state = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=enums.ListingStatesEnum,
        verbose_name="Статус листинга",
    )
    who_made = models.CharField(
        max_length=30,
        blank=True,
        choices=enums.WhoMadeEnum,
        default=enums.WhoMadeEnum.someone_else,
        verbose_name="Создатель листинга",
    )
    when_made = models.CharField(
        max_length=30,
        blank=True,
        choices=enums.WhenMadeEnum,
        default=enums.WhenMadeEnum.made_to_order,
        verbose_name="Период создания листинга",
    )
    is_supply = models.BooleanField(
        blank=True, default=False, verbose_name="Is supply",
    )
    has_variations = models.BooleanField(
        blank=True, default=False, verbose_name="Листинг имеет вариации",
    )
    language = models.CharField(
        max_length=5, default="en-US", verbose_name="Код языка локализации",
    )
    is_digital = models.BooleanField(
        blank=True, default=False, verbose_name="Листинг предназначен для скачивания",
    )
    url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="URL листинга на сайте Etsy",
    )

    views = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Количество просмотров листинга",
    )
    num_favorers = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Количество лайков листинга",
    )
    _style = models.TextField(default="[]", verbose_name="Стиль",)
    file_data = models.TextField(
        max_length=500, blank=True, null=True, verbose_name="Описание цифровых файлов"
    )
    is_customizable = models.BooleanField(
        blank=True, default=False, verbose_name="Товар кастомизируем",
    )

    _tags = models.TextField(default="[]", verbose_name="Теги")
    _materials = models.TextField(default="[]", verbose_name="Материалы")

    # non_taxable
    # should_auto_renew

    # item_weight
    # item_weight_unit
    # item_weight_length
    # item_weight_width
    # item_weight_height
    # item_weight_dimensions_unit

    # recipient
    # occasion
    # processing_min
    # processing_max
    # featured_rank

    objects = EtsyListingManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Листинг Etsy"
        verbose_name_plural = "Листинги Etsy"

    @property
    def style(self):
        return json.loads(self._style)

    @style.setter
    def style(self, values: list):
        self._style = json.dumps(values)

    @property
    def tags(self):
        return json.loads(self._tags)

    @tags.setter
    def tags(self, values: list):
        self._tags = json.dumps(values)

    @property
    def materials(self):
        return json.loads(self._tags)

    @materials.setter
    def materials(self, values: list):
        self._materials = json.dumps(values)
