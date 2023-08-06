from ebay.data import enums
from ebay.order import models
from ebay.order.serializers.api import (
    CancelStatusSerializer,
    FulfillmentStartInstructionSerializer,
    LineItemSerializer,
    PaymentSummarySerializer,
    PricingSummarySerializer,
)
from ebay.order.serializers.api.helpers import (
    update_or_create_cancel_status,
    update_or_create_ebay_order,
    update_or_create_fulfillment_start_instruction,
    update_or_create_line_item,
    update_or_create_payment_summary,
    update_or_create_pricing_summary,
)
from rest_framework import serializers


class BuyerSerializer(serializers.Serializer):
    username = serializers.CharField()


class EbayOrderSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer()
    cancelStatus = CancelStatusSerializer(source="cancel_status")
    fulfillmentHrefs = serializers.ListField(required=False, source="fulfillment_hrefs")
    fulfillmentStartInstructions = FulfillmentStartInstructionSerializer(
        many=True, source="fulfillment_start_instructions"
    )
    lineItems = LineItemSerializer(many=True)
    orderFulfillmentStatus = serializers.ChoiceField(
        choices=enums.OrderFulfillmentStatus
    )
    orderPaymentStatus = serializers.ChoiceField(choices=enums.OrderPaymentStatusEnum)
    paymentSummary = PaymentSummarySerializer(source="payment_summary")
    pricingSummary = PricingSummarySerializer(source="pricing_summary")
    salesRecordReference = serializers.CharField(required=False)

    class Meta:
        model = models.EbayOrder
        fields = [
            "marketplace_user_account",
            "buyer",
            "buyerCheckoutNotes",
            "cancelStatus",
            "creationDate",
            "ebayCollectAndRemitTax",
            "fulfillmentHrefs",
            "fulfillmentStartInstructions",
            "lastModifiedDate",
            "legacyOrderId",
            "lineItems",
            "orderFulfillmentStatus",
            "orderId",
            "orderPaymentStatus",
            "paymentSummary",
            "pricingSummary",
            "salesRecordReference",
            "sellerId",
        ]

    def create(self, validated_data):
        # Pop related data before EbayOrder create or update
        cancel_status_data = validated_data.pop("cancel_status")
        fulfillment_start_instruction_data_list = validated_data.pop(
            "fulfillment_start_instructions"
        )
        line_item_data_list = validated_data.pop("lineItems")
        payment_summary_data = validated_data.pop("payment_summary")
        pricing_summary_data = validated_data.pop("pricing_summary")
        # EbayOrder
        marketplace_user_account = validated_data.pop("marketplace_user_account")
        order_id = validated_data.pop("orderId")
        legacy_order_id = validated_data.pop("legacyOrderId")
        buyer = validated_data.pop("buyer")  # Buyer
        validated_data["buyer_username"] = buyer["username"]
        ebay_order, created = update_or_create_ebay_order(
            marketplace_user_account=marketplace_user_account,
            orderId=order_id,
            legacyOrderId=legacy_order_id,
            defaults=validated_data,
        )
        # CancelStatus & CancelRequest models update or create
        if cancel_status_data:
            update_or_create_cancel_status(ebay_order, cancel_status_data)
        # FulfillmentStartInstruction, FinalDestinationAddress,
        # ShippingStep, ShipTo & ContactAddress models update or create
        if fulfillment_start_instruction_data_list:
            for (
                fulfillment_start_instruction
            ) in fulfillment_start_instruction_data_list:
                update_or_create_fulfillment_start_instruction(
                    ebay_order, fulfillment_start_instruction
                )
        # EbayOrderLineItem, AppliedPromotion, DiscountAmount, LineItemDeliveryCost,
        # ImportCharges, ShippingCost, ShippingIntermediationFee,
        # DiscountedLineItemCost, LineItemCost, LineItemFulfillmentInstructions,
        # LineItemProperties, LineItemRefund, LineItemRefundAmount, LineItemTax,
        # LineItemTaxAmount & LineItemTotal models update or create
        if line_item_data_list:
            for line_item_data in line_item_data_list:
                update_or_create_line_item(order=ebay_order, data=line_item_data)
        # PaymentSummary, Payment, PaymentAmount, PaymentHold, HoldAmount,
        # SellerActionsToRelease, OrderRefund, OrderRefundAmount,
        # TotalDueSeller models update or create
        if payment_summary_data:
            update_or_create_payment_summary(
                order=ebay_order, data=payment_summary_data
            )
        # PricingSummary, Adjustment, DeliveryCost, DeliveryDiscount, Fee,
        # PriceDiscountSubtotal, PriceSubtotal, Tax & Total update or create
        if pricing_summary_data:
            update_or_create_pricing_summary(
                order=ebay_order, data=pricing_summary_data
            )
        return ebay_order
