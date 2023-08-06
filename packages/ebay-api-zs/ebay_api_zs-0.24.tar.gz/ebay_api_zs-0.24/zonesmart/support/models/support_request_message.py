from django.db import models

from model_utils.models import TimeStampedModel

from zonesmart.models import UUIDModel
from zonesmart.support.models import SupportRequest
from zonesmart.users.models import User


class SupportRequestMessage(TimeStampedModel, UUIDModel):
    support_request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name="messages",
        related_query_name="message",
        verbose_name="Заявка",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор сообщения"
    )
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Сообщение для ответа",
    )
    message = models.TextField(max_length=1500, verbose_name="Сообщение")

    def save(self, *args, **kwargs):
        if self.author == self.support_request.creator:
            new_support_request_status = self.support_request.STATUS.WAITING_FOR_HELPER
        else:
            new_support_request_status = self.support_request.STATUS.WAITING_FOR_USER
        # Change support request status only if it's changed
        if self.support_request.status != new_support_request_status:
            self.support_request.status = new_support_request_status
            self.support_request.save()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["modified"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
