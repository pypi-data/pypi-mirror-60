from django.db import models

from etsy_oauth.oauth_client import EtsyOAuthToken

from zonesmart.marketplace.models import MarketplaceUserAccount
from zonesmart.models import UUIDModel


class EtsyUserAccount(UUIDModel):
    marketplace_user_account = models.OneToOneField(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        related_name="etsy_user_account",
    )

    access_token = models.CharField(max_length=50, verbose_name="Токен доступа")
    access_token_secret = models.CharField(
        max_length=50, verbose_name="Секрет токена доступа"
    )

    sandbox = models.BooleanField(verbose_name="Аккаунт для Etsy Sandbox")

    @property
    def activated(self):
        return bool(self.access_token) and bool(self.access_token_secret)

    @property
    def token(self):
        if self.access_token and self.access_token_secret:
            return EtsyOAuthToken(self.access_token, self.access_token_secret)
        return None

    def __str__(self):
        return f'Токен доступа для Etsy пользователя "{self.marketplace_user_account.user}"'

    class Meta:
        verbose_name = "Пользовательский аккаунт Etsy"
        verbose_name_plural = "Пользовательские аккаунт Etsy"


class EtsyUserAccountInfo(UUIDModel):
    etsy_account = models.OneToOneField(
        EtsyUserAccount,
        on_delete=models.CASCADE,
        related_name="user_info",
        verbose_name="Пользовательский аккаунт Etsy",
    )
    # Fields
    user_id = models.CharField(
        max_length=30, unique=True, verbose_name="ID пользователя",
    )
    login_name = models.CharField(
        max_length=50, unique=True, verbose_name="Логин пользователя",
    )
    primary_email = models.EmailField(
        blank=True, null=True, verbose_name="E-mail пользователя",
    )
    feedback_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Количество оценок",
    )
    feedback_score = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Процент положительных оценок",
    )
    creation_tsz = models.DateTimeField(verbose_name="Дата и время регистрации",)

    def __str__(self):
        return f"Пользователь {self.login_name}"

    class Meta:
        verbose_name = "Информация об аккаунте"
        verbose_name_plural = verbose_name
