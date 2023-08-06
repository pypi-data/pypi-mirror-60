from rest_framework import serializers

from zonesmart.marketplace.models import Marketplace


class MarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplace
        fields = [
            "id",
            "name",
            "icon",
            "description",
        ]
