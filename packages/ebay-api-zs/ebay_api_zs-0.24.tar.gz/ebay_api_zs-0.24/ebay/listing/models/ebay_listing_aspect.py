from django.db import models

from ebay.listing.models import AbstractEbayAspect, EbayListing


class EbayListingAspect(AbstractEbayAspect):
    listing = models.ForeignKey(
        EbayListing,
        on_delete=models.CASCADE,
        related_name="aspects",
        related_query_name="aspect",
        verbose_name="eBay listing",
    )

    class Meta:
        verbose_name = "Аспект товара для eBay"
        verbose_name_plural = "Аспекты товара для eBay"
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "name", "value"],
                name="unique_listing_aspect_name_and_value",
            )
        ]
