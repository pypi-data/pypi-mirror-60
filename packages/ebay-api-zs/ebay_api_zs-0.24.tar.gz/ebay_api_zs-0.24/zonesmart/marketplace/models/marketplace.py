from django.db import models

from zonesmart.utils.upload import get_marketplace_icon_upload_path


class AmazonMarketplaceManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                unique_name__in=[
                    "amazon_europe",
                    "amazon_north_america",
                    "amazon_far_east",
                ]
            )
        )


class Marketplace(models.Model):
    name = models.CharField(
        max_length=50, unique=True, verbose_name="Название маркетплейса"
    )
    unique_name = models.CharField(max_length=50, unique=True,)
    icon = models.ImageField(
        upload_to=get_marketplace_icon_upload_path,
        blank=True,
        null=True,
        verbose_name="Иконка маркетплейса",
    )
    description = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="Описание маркетплейса"
    )
    # Managers
    objects = models.Manager()
    amazon = AmazonMarketplaceManager()

    class Meta:
        verbose_name = "Маркетплейс"
        verbose_name_plural = "Маркетплейсы"

    def __str__(self):
        return self.name
