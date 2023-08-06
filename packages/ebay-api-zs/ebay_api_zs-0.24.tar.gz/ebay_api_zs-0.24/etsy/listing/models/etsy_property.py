from django.db import models

from etsy.listing.models import EtsyListing, EtsyProduct

from zonesmart.models import UUIDModel


class AbstractEtsyProperty(UUIDModel):
    property_id = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="ID атрибута",
    )
    property_name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Название атрибута",
    )
    scale_id = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Scale ID",
    )
    scale_name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Scale name",
    )
    value_ids = models.CharField(max_length=500, verbose_name="Список ID значений",)
    values = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="Список значений",
    )

    def __str__(self):
        return f"{self.property_name} ({self.property_id})"

    class Meta:
        abstract = True


class EtsyListingAttribute(AbstractEtsyProperty):
    listing = models.ForeignKey(
        EtsyListing,
        on_delete=models.CASCADE,
        related_name="attributes",
        related_query_name="attribute",
    )


class EtsyProductProperty(AbstractEtsyProperty):
    product = models.ForeignKey(
        EtsyProduct,
        on_delete=models.CASCADE,
        related_name="properties",
        related_query_name="property",
    )
