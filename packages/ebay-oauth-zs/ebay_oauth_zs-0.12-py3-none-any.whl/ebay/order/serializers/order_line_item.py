from ebay.order.models import (
    AppliedPromotion,
    DiscountAmount,
    DiscountedLineItemCost,
    EbayOrderLineItem,
    ImportCharges,
    LineItemCost,
    LineItemDeliveryCost,
    LineItemFulfillmentInstructions,
    LineItemProperties,
    LineItemRefund,
    LineItemRefundAmount,
    ShippingCost,
    ShippingIntermediationFee,
)
from rest_framework import serializers


class DiscountAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountAmount
        exclude = ["id", "applied_promotion"]


class AppliedPromotionSerializer(serializers.ModelSerializer):
    discount_amount = DiscountAmountSerializer(required=False)

    class Meta:
        model = AppliedPromotion
        exclude = ["id", "line_item"]


class ShippingIntermediationFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingIntermediationFee
        exclude = ["id", "delivery_cost"]


class ShippingCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCost
        exclude = ["id", "delivery_cost"]


class ImportChargesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportCharges
        exclude = ["id", "delivery_cost"]


class LineItemDeliveryCostSerializer(serializers.ModelSerializer):
    import_charges = ImportChargesSerializer(required=False)
    shipping_cost = ShippingCostSerializer(required=False)
    shipping_intermediation_fee = ShippingIntermediationFeeSerializer(required=False)

    class Meta:
        model = LineItemDeliveryCost
        exclude = ["id", "line_item"]


class DiscountedLineItemCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountedLineItemCost
        exclude = ["id", "line_item"]


class LineItemCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItemCost
        exclude = ["id", "line_item"]


class LineItemFulfillmentInstructionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItemFulfillmentInstructions
        exclude = ["id", "line_item"]


class LineItemPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItemProperties
        exclude = ["id", "line_item"]


class LineItemRefundAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItemRefundAmount
        exclude = ["id", "line_item_refund"]


class LineItemRefundSerializer(serializers.ModelSerializer):
    amount = LineItemRefundAmountSerializer(required=False)

    class Meta:
        model = LineItemRefund
        exclude = ["id", "line_item"]


class EbayOrderLineItemSerializer(serializers.ModelSerializer):
    applied_promotions = AppliedPromotionSerializer(required=False, many=True)
    delivery_cost = LineItemDeliveryCostSerializer(required=False)
    discounted_line_item_cost = DiscountedLineItemCostSerializer(required=False)
    line_item_cost = LineItemCostSerializer(required=False)
    line_item_fulfillment_instructions = LineItemFulfillmentInstructionsSerializer(
        required=False
    )
    properties = LineItemPropertiesSerializer(required=False)
    refunds = LineItemRefundSerializer(required=False, many=True)

    class Meta:
        model = EbayOrderLineItem
        exclude = ["id", "order"]
