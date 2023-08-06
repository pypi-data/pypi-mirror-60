from rest_framework import viewsets

from zonesmart.marketplace.models import Marketplace
from zonesmart.marketplace.serializers.marketplace import MarketplaceSerializer


class MarketplaceReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MarketplaceSerializer
    queryset = Marketplace.objects.all()
    lookup_field = "id"
