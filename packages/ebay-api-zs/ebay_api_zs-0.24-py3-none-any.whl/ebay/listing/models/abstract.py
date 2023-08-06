from django.db import models

from zonesmart.models import UUIDModel


class AbstractEbayAspect(UUIDModel):
    name = models.CharField(max_length=40, verbose_name="Name")
    value = models.CharField(max_length=50, verbose_name="Value")

    class Meta:
        abstract = True
