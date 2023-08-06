from django.contrib import admin

import nested_admin

from zonesmart.product.models import BaseProduct, ProductCodeType, ProductImage


@admin.register(BaseProduct)
class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ["title", "user"]
    list_filter = ["user"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductCodeType)
class ProductCodeTypeAdmin(admin.ModelAdmin):
    pass
