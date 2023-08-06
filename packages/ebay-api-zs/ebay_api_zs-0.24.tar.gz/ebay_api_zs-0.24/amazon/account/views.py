from amazon.account.serializers.amazon_user_account import (
    BaseAmazonUserAccountSerializer,
    CreateAmazonUserAccountSerializer,
)
from rest_framework import mixins, viewsets

from zonesmart.views import GenericSerializerViewSet


class AmazonUserAccountViewSet(
    mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet, GenericSerializerViewSet
):
    serializer_classes = {
        "default": BaseAmazonUserAccountSerializer,
        "create": CreateAmazonUserAccountSerializer,
    }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(marketplace_user_account__user=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
