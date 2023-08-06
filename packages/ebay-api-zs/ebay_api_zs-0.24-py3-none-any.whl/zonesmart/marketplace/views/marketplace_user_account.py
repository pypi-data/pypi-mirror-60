from rest_framework import viewsets

from zonesmart.marketplace.serializers import MarketplaceUserAccountSerializer


class MarketplaceUserAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MarketplaceUserAccountSerializer
    lookup_field = "id"

    def get_queryset(self):
        return self.request.user.marketplace_accounts.all()
