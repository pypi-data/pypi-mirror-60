from django.db import models


class ProductCodeType(models.Model):
    name = models.CharField(max_length=10, verbose_name="Наименование")
    description = models.CharField(max_length=100, verbose_name="Описание")

    class Meta:
        verbose_name = "Тип кода товара"
        verbose_name_plural = "Типы кодов товара"

    def __str__(self):
        return self.name
