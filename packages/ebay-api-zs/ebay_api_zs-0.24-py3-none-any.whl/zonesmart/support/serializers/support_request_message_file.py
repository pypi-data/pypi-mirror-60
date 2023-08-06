from rest_framework import serializers

from zonesmart.support.models import SupportRequestMessageFile


class SupportRequestMessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequestMessageFile
        fields = ["id", "file"]
        read_only_fields = ["id"]
