from collections import OrderedDict

from rest_framework import serializers


class NotNullAndEmptyStringSerializer(
    serializers.Serializer
):  # не проходится по вложениям?
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return OrderedDict(
            [
                (key, representation[key])
                for key in representation
                if representation[key] not in [None, "", [], {}]
            ]
        )


class NotNullAndEmptyStringModelSerializer(
    NotNullAndEmptyStringSerializer, serializers.ModelSerializer
):
    pass


class RecursiveField(serializers.Serializer):  # не используется
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


class ModelSerializerWithoutNullAndEmptyObjects(serializers.ModelSerializer):
    def clean_representation(self, representation: dict) -> dict:
        cleaned_representation = dict()
        if type(representation) is OrderedDict:
            representation = dict(representation)
            for key, value in representation.items():
                if value not in ["", None, list(), dict()]:
                    cleaned_representation[key] = self.clean_representation(value)
        else:
            cleaned_representation = representation
        return cleaned_representation
