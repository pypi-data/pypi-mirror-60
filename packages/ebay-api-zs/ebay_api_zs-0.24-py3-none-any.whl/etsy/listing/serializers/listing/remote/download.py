from datetime import datetime

from django.utils.timezone import make_aware

from etsy.listing.serializers.listing.base import BaseEtsyProductSerializer
from etsy.listing.serializers.listing.remote.base import BaseEtsyListingSerializer


class DownloadEtsyProductSerializer(BaseEtsyProductSerializer):
    class Meta(BaseEtsyProductSerializer.Meta):
        extra_kwargs = {
            "product_id": {"validators": []},
            "offering_id": {"validators": []},
        }


class DownloadEtsyListingSerializer(BaseEtsyListingSerializer):
    products = DownloadEtsyProductSerializer(many=True)

    class Meta(BaseEtsyListingSerializer.Meta):
        exclude = BaseEtsyListingSerializer.Meta.exclude + [
            "channel",
            "base_product",
            "shop_section",
            "category",
        ]
        extra_kwargs = {"listing_id": {"validators": []}}

    def to_internal_value(self, data):
        for field in [
            "creation_tsz",
            "ending_tsz",
            "original_creation_tsz",
            "last_modified_tsz",
            "state_tsz",
        ]:
            if field in data:
                data[field] = make_aware(datetime.fromtimestamp(data[field]))
        return super().to_internal_value(data)

    def create(self, validated_data):
        channel = validated_data.pop("channel")
        listing_id = validated_data.pop("listing_id")
        instance, updated = self.Meta.model.objects.update_or_create(
            channel=channel, listing_id=listing_id, defaults=validated_data
        )
        return instance
