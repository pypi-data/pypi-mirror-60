from django.db import models


class EtsyCountry(models.Model):
    country_id = models.PositiveSmallIntegerField(
        primary_key=True, verbose_name="ID страны",
    )
    iso_country_code = models.CharField(max_length=2, verbose_name="Код страны (ISO)",)
    world_bank_country_code = models.CharField(
        max_length=3, blank=True, null=True, verbose_name="Код страны (мировой банк)",
    )
    name = models.CharField(max_length=50, verbose_name="Название страны",)
    slug = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Slug страны",
    )
    lat = models.FloatField(blank=True, null=True, verbose_name="Широта",)
    lon = models.FloatField(blank=True, null=True, verbose_name="Долгота",)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class EtsyRegion(models.Model):
    region_id = models.PositiveSmallIntegerField(
        primary_key=True, verbose_name="ID региона",
    )
    region_name = models.CharField(max_length=50, verbose_name="Название страны",)
