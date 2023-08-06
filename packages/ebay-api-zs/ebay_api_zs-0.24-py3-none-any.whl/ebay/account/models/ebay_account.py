from django.db import models
from django.utils import timezone

import pytz
from ebay_oauth.model import oAuth_token

from zonesmart.marketplace.models import MarketplaceUserAccount
from zonesmart.models import UUIDModel


class AbstractEbayAccount(UUIDModel):
    access_token = models.CharField(
        max_length=2500, blank=True, default="", verbose_name="Токен доступа"
    )
    access_token_expiry = models.DateTimeField(
        blank=True, default=timezone.now, verbose_name="Токен доступа годен до"
    )
    refresh_token = models.CharField(
        max_length=2500, blank=True, default="", verbose_name="Токен обновления"
    )
    refresh_token_expiry = models.DateTimeField(
        blank=True, default=timezone.now, verbose_name="Токен обновления годен до"
    )
    sandbox = models.BooleanField(verbose_name="Аккаунт eBay Sandbox",)

    def access_token_expired(self):
        return self.access_token_expiry < timezone.now()

    def save_token_data(self, token_data: oAuth_token):
        utc = pytz.timezone("UTC")
        self.access_token = token_data.access_token
        self.access_token_expiry = timezone.localtime(
            timezone.make_aware(token_data.token_expiry, utc)
        )
        if token_data.refresh_token:
            self.refresh_token = token_data.refresh_token
        if token_data.refresh_token_expiry:
            self.refresh_token_expiry = timezone.localtime(
                timezone.make_aware(token_data.refresh_token_expiry, utc)
            )
        self.save()

    class Meta:
        abstract = True


class EbayAppAccount(AbstractEbayAccount):
    def __str__(self):
        return f'Аккаунт eBay уровня приложения ({"sandbox" if self.sandbox else "production"})'

    class Meta:
        verbose_name = "Аккаунт eBay уровня приложения"
        verbose_name_plural = "Аккаунты eBay уровня приложения"


class EbayUserAccount(AbstractEbayAccount):
    marketplace_user_account = models.OneToOneField(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        related_name="ebay_user_account",
    )

    def __str__(self):
        return (
            f'Аккаунт eBay уровня пользователя (пользователь: "{self.marketplace_user_account.user}")'
            f' ({"sandbox" if self.sandbox else "production"})'
        )

    @property
    def user(self):
        return self.marketplace_user_account.user

    class Meta:
        verbose_name = "Аккаунт для eBay уровня пользователя"
        verbose_name_plural = "Аккаунты для eBay уровня пользователя"
