from django.contrib import admin

from etsy.models import EtsyCountry, EtsyRegion


@admin.register(EtsyCountry)
class EtsyCountryAdmin(admin.ModelAdmin):
    pass


@admin.register(EtsyRegion)
class EtsyRegionAdmin(admin.ModelAdmin):
    pass
