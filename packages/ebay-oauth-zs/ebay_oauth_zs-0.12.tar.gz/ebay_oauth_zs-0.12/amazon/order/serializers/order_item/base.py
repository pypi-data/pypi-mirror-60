from amazon.order.models import AmazonOrderItem
from rest_framework import serializers


class MoneySerializer(serializers.Serializer):
    CurrencyCode = serializers.CharField()
    Amount = serializers.FloatField()


class BaseAmazonOrderItemSerializer(serializers.ModelSerializer):
    ItemPrice = MoneySerializer(required=False, source="item_price")
    ShippingPrice = MoneySerializer(required=False, source="shipping_price")
    GiftWrapPrice = MoneySerializer(required=False, source="gift_wrap_price")
    ItemTax = MoneySerializer(required=False, source="item_tax")
    ShippingTax = MoneySerializer(required=False, source="shipping_tax")
    GiftWrapTax = MoneySerializer(required=False, source="gift_wrap_tax")
    ShippingDiscount = MoneySerializer(required=False, source="shipping_discount")
    PromotionDiscount = MoneySerializer(required=False, source="promotion_discount")

    class Meta:
        model = AmazonOrderItem
        exclude = [
            "order",
        ]

    def create(self, validated_data):
        return super().create(validated_data)
