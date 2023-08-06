from etsy.models import EtsyCountry, EtsyRegion
from rest_framework import serializers


class BaseEtsyCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyCountry
        fields = [
            "country_id",
            "iso_country_code",
            "world_bank_country_code",
            "name",
        ]


class BaseEtsyRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyRegion
        fields = [
            "region_id",
            "region_name",
        ]
