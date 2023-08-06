from django.db import models

from etsy.account.models import EtsyUserAccount
from etsy.data.enums import ChargeTypeEnum, CurrencyCodeEnum


class EtsyBillCharge(models.Model):
    """
    Represents a charge to an Etsy member's account.

    Docs:
    https://www.etsy.com/developers/documentation/reference/billcharge
    """

    etsy_user_account = models.ForeignKey(
        EtsyUserAccount,
        on_delete=models.CASCADE,
        related_name="bill_charges",
        related_query_name="bill_charge",
    )
    # Fields
    bill_charge_id = models.CharField(
        max_length=20, primary_key=True, verbose_name="ID"
    )
    creation_tsz = models.DateTimeField(verbose_name="Дата и время создания")
    last_modified_tsz = models.DateTimeField(verbose_name="Дата и время обновления")
    bill_type = models.CharField(
        max_length=30, choices=ChargeTypeEnum, verbose_name="Тип списания"
    )
    bill_type_id = models.CharField(
        max_length=20, verbose_name="ID объекта связанного со списанием"
    )
    amount = models.FloatField(verbose_name="Сумма списания")
    currency_code = models.CharField(
        max_length=3, choices=CurrencyCodeEnum, verbose_name="Код валюты"
    )
    # Not used fields
    # creation_year - Year that the charge was created.
    # creation_month - Month that the charge was created.

    class Meta:
        verbose_name = "Списание по аккаунту Etsy"
        verbose_name_plural = "Списания по аккаунтам Etsy"

    def __str__(self):
        return f"Списание по аккаунту Etsy {self.bill_charge_id}"


class EtsyUserBillingOverview(models.Model):
    """
    A user's account balance on Etsy.

    Docs:
    https://www.etsy.com/developers/documentation/reference/billingoverview
    """

    etsy_user_account = models.OneToOneField(
        EtsyUserAccount,
        on_delete=models.CASCADE,
        related_name="billing_overview",
        verbose_name="Пользовательский аккаунт Etsy",
    )
    # Fields
    is_overdue = models.BooleanField(verbose_name="Баланс просрочен")
    currency_code = models.CharField(
        max_length=3, choices=CurrencyCodeEnum, verbose_name="Код валюты"
    )
    overdue_balance = models.FloatField(verbose_name="Сумма просроченного баланса")
    balance_due = models.FloatField(
        verbose_name="Общая сумма, подлежащая оплате в настоящее время (включая просроченный остаток)"
    )
    total_balance = models.FloatField(
        verbose_name="Общая сумма, причитающаяся пользователю (включая сборы, которые еще не подлежат оплате)"
    )
    date_due = models.DateTimeField(
        verbose_name="Дата, к которой баланс должен быть оплачен"
    )

    class Meta:
        verbose_name = "Информация о балансе аккаунта Etsy"
        verbose_name_plural = "Информация о балансах аккаунтов Etsy"

    def __str__(self):
        return f"Баланс аккаунта {self.etsy_user_account.id} - {self.total_balance}"
