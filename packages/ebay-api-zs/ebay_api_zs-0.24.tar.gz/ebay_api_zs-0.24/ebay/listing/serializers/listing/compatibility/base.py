from ebay.listing.models import (
    EbayProductCompatibility,
    EbayProductCompatibilityProperty,
)
from rest_framework import serializers


class BaseEbayProductCompatibilityPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = EbayProductCompatibilityProperty
        exclude = ["id", "compatibility"]


class BaseEbayProductCompatibilitySerializer(serializers.ModelSerializer):
    REQUIRED_PROPERTIES = ["Make", "Model", "Year"]

    properties = BaseEbayProductCompatibilityPropertySerializer(
        many=True, allow_null=False
    )

    class Meta:
        model = EbayProductCompatibility
        fields = ["notes", "epid", "ktype", "properties"]

    def to_internal_value(self, data):
        print(data["properties"])
        data["properties"] = [
            {"name": prop["name"], "value": prop["value"],}
            for prop in data["properties"]
        ]
        return super().to_internal_value(data)

    def to_representation(self, instance: EbayProductCompatibility):
        representation = super().to_representation(instance)
        representation["properties"] = {
            p["name"]: p["value"] for p in representation["properties"]
        }
        return representation

    def validate_properties(self, property_list):
        # Get names of properties to create
        property_name_list = [property_data["name"] for property_data in property_list]
        # Check if all required properties in properties dict
        if not all(
            required_property in property_name_list
            for required_property in self.REQUIRED_PROPERTIES
        ):
            required_property_name_list = ", ".join(
                name
                for name in self.REQUIRED_PROPERTIES
                if name not in property_name_list
            )
            raise serializers.ValidationError(
                f"Missing required properties: {required_property_name_list}."
            )
        return property_list
