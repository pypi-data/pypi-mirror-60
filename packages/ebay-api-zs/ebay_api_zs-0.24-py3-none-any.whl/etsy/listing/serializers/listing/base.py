from etsy.listing.models import EtsyListing, EtsyProduct
from rest_framework import serializers


class BaseEtsyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyProduct
        exclude = ["listing"]


class BaseEtsyListingSerializer(serializers.ModelSerializer):
    products = BaseEtsyProductSerializer(many=True)
    style = serializers.ListField(required=False)

    class Meta:
        model = EtsyListing
        fields = "__all__"
