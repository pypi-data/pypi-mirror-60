from cities_light.models import Country, City, Region
from django.contrib.auth import get_user_model
from django.db import models

from model_utils.managers import InheritanceManager

from zonesmart.marketplace.models import Marketplace

User = get_user_model()


class BaseOrder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="base_orders",
        related_query_name="base_order",
        verbose_name="Пользователь",
    )
    # Fields
    marketplace = models.ForeignKey(
        Marketplace,
        on_delete=models.CASCADE,
        related_name="orders",
        related_query_name="order",
        verbose_name="Маркетплейс",
    )
    create_date = models.DateTimeField(verbose_name="Дата и время создания")
    update_date = models.DateTimeField(verbose_name="Дата и время обновления")
    # Payment
    is_paid = models.BooleanField(verbose_name="Оплачен")
    paid_info = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Информация об оплате"
    )
    # Shipping
    is_shipped = models.BooleanField(verbose_name="Отправлен")
    shipped_info = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Информация о доставке"
    )
    shipping_method = models.CharField(max_length=255, verbose_name="Тип доставки")
    # Buyer
    buyer = models.CharField(max_length=255, verbose_name="Покупатель")
    # Price
    total_price = models.FloatField(verbose_name="Итоговая сумма")
    # Custom inheritance manager
    objects = InheritanceManager()

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ с маркетплейса {self.marketplace}"


class BaseOrderItem(models.Model):
    order = models.ForeignKey(
        BaseOrder,
        on_delete=models.CASCADE,
        related_name="items",
        related_query_name="item",
        verbose_name="Заказ",
    )
    # Fields
    sku = models.CharField(max_length=255, verbose_name="SKU товара")
    title = models.CharField(max_length=255, verbose_name="Наименование товара")

    class Meta:
        verbose_name = "Предмет из заказа"
        verbose_name_plural = "Предметы из заказов"

    def __str__(self):
        return f"Предмет из заказа {self.order.id}"


class ShippingAddress(models.Model):
    order = models.OneToOneField(
        BaseOrder,
        on_delete=models.CASCADE,
        related_name="ship_to",
        verbose_name="Заказ",
    )
    # Fields
    first_line = models.CharField(max_length=255, verbose_name="Первая строка адреса")
    second_line = models.CharField(max_length=255, verbose_name="Вторая строка адреса")
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
        verbose_name="Город",
    )
    state = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
        verbose_name="Область",
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
        verbose_name="Страна",
    )
    zip_code = models.CharField(max_length=255, verbose_name="Почтовый индекс")

    class Meta:
        verbose_name = "Адрес доставки"
        verbose_name_plural = "Адреса доставки"

    def __str__(self):
        return f"Адрес доставки для заказа №{self.order.id}"
