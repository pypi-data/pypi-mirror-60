from ebay.order.models import (
    Adjustment,
    DeliveryCost,
    DeliveryDiscount,
    Fee,
    PriceDiscountSubtotal,
    PriceSubtotal,
    PricingSummary,
    Tax,
    Total,
)
from rest_framework import serializers


class TotalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Total
        exclude = ["id", "pricing_summary"]


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        exclude = ["id", "pricing_summary"]


class PriceSubtotalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceSubtotal
        exclude = ["id", "pricing_summary"]


class PriceDiscountSubtotalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceDiscountSubtotal
        exclude = ["id", "pricing_summary"]


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        exclude = ["id", "pricing_summary"]


class DeliveryDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDiscount
        exclude = ["id", "pricing_summary"]


class DeliveryCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCost
        exclude = ["id", "pricing_summary"]


class AdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adjustment
        exclude = ["id", "pricing_summary"]


class PricingSummarySerializer(serializers.ModelSerializer):
    adjustment = AdjustmentSerializer(required=False)
    delivery_cost = DeliveryCostSerializer(required=False)
    delivery_discount = DeliveryDiscountSerializer(required=False)
    fee = FeeSerializer(required=False)
    price_discount_subtotal = PriceDiscountSubtotalSerializer(required=False)
    price_subtotal = PriceSubtotalSerializer(required=False)
    tax = TaxSerializer(required=False)
    total = TotalSerializer(required=False)

    class Meta:
        model = PricingSummary
        exclude = ["id", "order"]
