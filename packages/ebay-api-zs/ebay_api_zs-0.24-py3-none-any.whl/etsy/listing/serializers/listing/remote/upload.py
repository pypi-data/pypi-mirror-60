from etsy.listing.models import EtsyListing, EtsyProduct, EtsyProductProperty
from rest_framework import serializers


class EtsyProductPropertySerializer(serializers.ModelSerializer):
    values = serializers.CharField(source="value_ids")

    class Meta:
        model = EtsyProductProperty
        fields = [
            "property_id",
            "values",
        ]


class EtsyProductOfferingSerializer(serializers.Serializer):
    price = serializers.FloatField()
    quantity = serializers.IntegerField()

    def to_representation(self, instance):
        return [super().to_representation(instance)]

    class Meta:
        fields = [
            "price",
            "quantity",
        ]


class EtsyProductSerializer(serializers.ModelSerializer):
    properties = EtsyProductPropertySerializer(many=True)
    offerings = EtsyProductOfferingSerializer(source="*")

    class Meta:
        model = EtsyProduct
        fields = [
            "sku",
            "offerings",
            "properties",
        ]


class RemoteCreateEtsyListingSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(source="total_quantity")
    taxonomy_id = serializers.IntegerField(source="category.category_id")
    products = EtsyProductSerializer(many=True)
    shipping_template_id = serializers.IntegerField(
        source="shipping_template.shipping_template_id"
    )

    class Meta:
        model = EtsyListing
        fields = [
            "listing_id",
            "quantity",
            "price",
            "title",
            "description",
            "taxonomy_id",
            "who_made",
            "when_made",
            "is_supply",
            "products",
            "materials",
            "shipping_template_id",
            "shop_section_id",
            # "image_ids",
            # "image",
            "state",
        ]
