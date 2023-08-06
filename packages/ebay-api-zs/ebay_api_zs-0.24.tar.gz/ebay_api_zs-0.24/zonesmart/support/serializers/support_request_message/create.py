from zonesmart.support.serializers.support_request_message import (
    BaseSupportRequestMessageSerializer,
)


class CreateSupportRequestMessageSerializer(BaseSupportRequestMessageSerializer):
    class Meta(BaseSupportRequestMessageSerializer.Meta):
        read_only_fields = [
            "id",
            "created",
            "author",
            "files",
        ]
