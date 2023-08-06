from ebay.location.serializers import BaseEbayLocationSerializer


class UpdateEbayLocationSerializer(BaseEbayLocationSerializer):
    class Meta(BaseEbayLocationSerializer.Meta):
        fields = [
            "name",
            "merchantLocationKey",
            "locationTypes",
            "phone",
            "addressLine1",
            "addressLine2",
            "city",
            "countryCode",
            "county",
            "postalCode",
            "stateOrProvince",
        ]
        read_only_fields = BaseEbayLocationSerializer.Meta.read_only_fields + [
            "locationTypes",
        ]
