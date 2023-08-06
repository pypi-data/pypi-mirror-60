from django.db import models

from zonesmart.marketplace.models import MarketplaceUserAccount
from zonesmart.models import UUIDModel


class AmazonUserAccount(UUIDModel):
    marketplace_user_account = models.OneToOneField(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        related_name="amazon_user_account",
    )
    access_token = models.CharField(max_length=2500, verbose_name="Токен доступа")

    def __str__(self):
        return f'Токен доступа для Amazon пользователя "{self.marketplace_user_account.user}"'

    class Meta:
        verbose_name = "Пользовательский токен для Amazon"
        verbose_name_plural = "Пользовательские токены для Amazon"
