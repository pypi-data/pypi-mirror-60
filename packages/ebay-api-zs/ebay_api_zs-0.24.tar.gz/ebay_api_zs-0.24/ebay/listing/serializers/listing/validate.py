from ebay.listing.models import EbayListingAspect, EbayProduct
from rest_framework import serializers


class ValidateEbayProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayProduct
        exclude = ["id", "listing"]


class ValidateEbayListingAspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayListingAspect
        exclude = ["id", "listing"]
