from django.contrib import admin

import nested_admin
from ebay.listing import models


class EbayProductCompatibilityPropertyInline(nested_admin.NestedTabularInline):
    model = models.EbayProductCompatibilityProperty
    can_delete = True
    extra = 0


@admin.register(models.EbayProductCompatibility)
class EbayProductCompatibilityAdmin(nested_admin.NestedModelAdmin):
    inlines = [
        EbayProductCompatibilityPropertyInline,
    ]


@admin.register(models.EbayListing)
class EbayListingAdmin(admin.ModelAdmin):
    pass
