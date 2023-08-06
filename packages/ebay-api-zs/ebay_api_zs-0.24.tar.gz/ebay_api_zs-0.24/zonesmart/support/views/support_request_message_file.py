from rest_framework import mixins, viewsets
from rest_framework.parsers import MultiPartParser

from zonesmart.support.serializers import SupportRequestMessageFileSerializer


class SupportRequestMessageFileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SupportRequestMessageFileSerializer
    parser_classes = [MultiPartParser]
    lookup_field = "id"

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            support_request_message_id=self.kwargs["support_request_message_id"]
        )

    def perform_create(self, serializer):
        serializer.save(
            support_request_message_id=self.kwargs["support_request_message_id"]
        )
