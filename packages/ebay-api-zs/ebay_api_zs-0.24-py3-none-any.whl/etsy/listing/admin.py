from django.contrib import admin

import nested_admin
from etsy.listing.models import (
    EtsyListing,
    EtsyListingAttribute,
    EtsyProduct,
    EtsyProductProperty,
)

# LISTING


class EtsyProductPropertyInline(nested_admin.NestedTabularInline):
    model = EtsyProductProperty
    can_delete = True
    extra = 0


class EtsyProductInline(nested_admin.NestedStackedInline):
    model = EtsyProduct
    can_delete = True
    extra = 0
    inlines = [EtsyProductPropertyInline]


class EtsyListingAttributeInline(nested_admin.NestedTabularInline):
    model = EtsyListingAttribute
    can_delete = True
    extra = 0


@admin.register(EtsyListing)
class EtsyListingAdmin(nested_admin.NestedModelAdmin):
    inlines = [EtsyProductInline, EtsyListingAttributeInline]
