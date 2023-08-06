from amazon.order.models import AmazonOrder, AmazonShippingAddress
from amazon.order.serializers.helpers.order import update_or_create_amazon_order
from rest_framework import serializers


class AmazonShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmazonShippingAddress
        exclude = ["id", "order"]


class OrderTotalSerializer(serializers.Serializer):
    Amount = serializers.CharField(required=False, source="OrderTotalAmount")
    CurrencyCode = serializers.CharField(
        required=False, source="OrderTotalCurrencyCode"
    )


class BuyerTaxInfoSerializer(serializers.Serializer):
    CompanyLegalName = serializers.CharField(required=False)
    TaxingRegion = serializers.CharField(required=False)


class BaseAmazonOrderSerializer(serializers.ModelSerializer):
    ShippingAddress = AmazonShippingAddressSerializer(
        required=False, source="shipping_address"
    )
    BuyerTaxInfo = BuyerTaxInfoSerializer(required=False)
    OrderTotal = OrderTotalSerializer(required=False, source="*", write_only=True)
    PaymentMethodDetails = serializers.ListField(
        required=False, source="payment_method_details"
    )

    class Meta:
        model = AmazonOrder
        exclude = ["CompanyLegalName", "TaxingRegion", "_payment_method_details"]

    def create(self, validated_data):
        channel = validated_data.pop("channel")
        order_id = validated_data.pop("AmazonOrderId")
        instance, created = update_or_create_amazon_order(
            channel=channel, AmazonOrderId=order_id, defaults=validated_data
        )
        return instance
