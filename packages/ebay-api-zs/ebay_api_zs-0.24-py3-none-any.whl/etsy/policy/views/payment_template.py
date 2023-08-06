from rest_framework import mixins

from etsy.policy.serializers.payment.base import BaseEtsyPaymentTemplateSerializer
from etsy.policy.serializers.payment.update import UpdateEtsyPaymentTemplateSerializer
from zonesmart.views import GenericSerializerViewSet


class PaymentTemplateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericSerializerViewSet,
):
    serializer_classes = {
        "default": BaseEtsyPaymentTemplateSerializer,
        "update": UpdateEtsyPaymentTemplateSerializer,
        "partial_update": UpdateEtsyPaymentTemplateSerializer,
    }
