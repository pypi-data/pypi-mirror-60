from django.contrib import admin

from ebay.location import models


@admin.register(models.EbayLocation)
class EbayLocationAdmin(admin.ModelAdmin):
    verbose_name = "Склад для eBay"
    verbose_name_plural = "Склады для eBay"
    list_display = ["name", "marketplace_user_account"]
    exclude = []
