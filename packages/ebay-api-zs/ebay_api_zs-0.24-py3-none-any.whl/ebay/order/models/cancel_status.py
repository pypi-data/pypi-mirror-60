from django.db import models

from ebay.data import enums
from ebay.order.models import EbayOrder


class CancelStatus(models.Model):
    order = models.OneToOneField(
        EbayOrder, on_delete=models.CASCADE, related_name="cancel_status"
    )
    # Fields
    cancelledDate = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата отмены заказа"
    )
    cancelState = models.CharField(max_length=14, choices=enums.CancelStateEnum)

    class Meta:
        verbose_name = "Статус отмены заказа"
        verbose_name_plural = "Статусы отменов заказов"


class CancelRequest(models.Model):
    cancel_status = models.ForeignKey(
        CancelStatus,
        on_delete=models.CASCADE,
        related_name="cancel_requests",
        related_query_name="cancel_request",
    )
    # Fields
    cancelCompletedDate = models.DateTimeField(blank=True, null=True)
    cancelInitiator = models.CharField(max_length=255, blank=True, null=True)
    cancelReason = models.CharField(max_length=255, blank=True, null=True)
    cancelRequestedDate = models.DateTimeField()
    cancelRequestId = models.CharField(max_length=255, blank=True, null=True)
    cancelRequestState = models.CharField(
        max_length=9, blank=True, null=True, choices=enums.CancelRequestStateEnum
    )

    class Meta:
        verbose_name = "Запрос на отмену заказа от покупателя"
        verbose_name_plural = "Запросы на отмену заказов от покупателей"
