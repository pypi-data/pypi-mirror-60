from django.db import models

from ebay.account.models import EbayUserAccount
from ebay.data import enums

from zonesmart.models import NestedUpdateOrCreateModelManager, UUIDModel


class EbayUserAccountProfile(UUIDModel):
    ebay_user_account = models.OneToOneField(
        EbayUserAccount, on_delete=models.CASCADE, related_name="profile"
    )
    # Fields
    ACCOUNT_TYPE_CHOICES = (
        ("BUSINESS", "BUSINESS"),
        ("INDIVIDUAL", "INDIVIDUAL"),
    )
    USER_STATUS_CHOICES = (
        ("CONFIRMED", "Верифицирован"),
        ("UNCONFIRMED", "Неверифицирован"),
        ("ACCOUNTONHOLD", "Ожидает верификации"),
        ("UNDETERMINED", "Другое"),
    )
    account_type = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Тип аккаунта",
    )
    registrationMarketplaceId = models.CharField(
        max_length=14, choices=enums.MarketplaceEnum, verbose_name="Домен регистрации",
    )
    status = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        choices=USER_STATUS_CHOICES,
        verbose_name="Статус аккаунта",
    )
    userId = models.CharField(max_length=50, verbose_name="ID пользователя",)
    username = models.CharField(max_length=100, verbose_name="Имя пользователя",)

    objects = NestedUpdateOrCreateModelManager()

    def __str__(self):
        return f"Профиль пользователя в eBay ({self.ebay_user_account})"

    class Meta:
        verbose_name = "Профиль пользователя в eBay"
        verbose_name_plural = "Профили пользователей в eBay"
