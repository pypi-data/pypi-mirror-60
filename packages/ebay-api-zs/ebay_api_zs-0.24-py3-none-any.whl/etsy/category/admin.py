from django.contrib import admin

from etsy.category.models import EtsyCategory, EtsyCategoryTree

from zonesmart.category.admin import (
    MarketplaceCategoryAdmin,
    MarketplaceCategoryTreeAdmin,
)


@admin.register(EtsyCategoryTree)
class EtsyCategoryTreeAdmin(MarketplaceCategoryTreeAdmin):
    pass


@admin.register(EtsyCategory)
class EtsyCategoryAdmin(MarketplaceCategoryAdmin):
    pass
