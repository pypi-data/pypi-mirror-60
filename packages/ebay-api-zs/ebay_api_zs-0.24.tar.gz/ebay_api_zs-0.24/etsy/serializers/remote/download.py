from etsy.serializers import BaseEtsyCountrySerializer, BaseEtsyRegionSerializer


class DownloadEtsyCountrySerializer(BaseEtsyCountrySerializer):
    class Meta(BaseEtsyCountrySerializer.Meta):
        extra_kwargs = {"country_id": {"validators": []}}

    def create(self, validated_data):
        country_id = validated_data.pop("country_id")
        instance, updated = self.Meta.model.objects.update_or_create(
            country_id=country_id, defaults=validated_data
        )
        return instance


class DownloadEtsyRegionSerializer(BaseEtsyRegionSerializer):
    class Meta(BaseEtsyRegionSerializer.Meta):
        extra_kwargs = {"region_id": {"validators": []}}

    def create(self, validated_data):
        region_id = validated_data.pop("region_id")
        instance, updated = self.Meta.model.objects.update_or_create(
            region_id=region_id, defaults=validated_data
        )
        return instance
