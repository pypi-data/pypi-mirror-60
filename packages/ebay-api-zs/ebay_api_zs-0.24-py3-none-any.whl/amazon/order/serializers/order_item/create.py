from amazon.order.models import AmazonOrderItem
from amazon.order.serializers.helpers.order_item import update_or_create_order_item
from amazon.order.serializers.order_item import BaseAmazonOrderItemSerializer


class CreateAmazonOrderItemSerializer(BaseAmazonOrderItemSerializer):
    class Meta(BaseAmazonOrderItemSerializer.Meta):
        exclude = ["id"]

    def create(self, validated_data):
        order = validated_data.pop("order")
        instance: AmazonOrderItem
        created: bool
        instance, created = update_or_create_order_item(
            order=order, data=validated_data
        )
        return instance
