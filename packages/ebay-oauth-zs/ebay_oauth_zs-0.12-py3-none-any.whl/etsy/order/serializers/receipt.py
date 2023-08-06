from django.utils import timezone

from rest_framework import serializers

from etsy.order.models import EtsyReceipt
from etsy.order.models.receipt import EtsyReceiptShippingDetails
from etsy.order.serializers.transaction import BaseReceiptTransactionSerializer


class BaseEtsyReceiptSerializer(serializers.ModelSerializer):
    transactions = BaseReceiptTransactionSerializer(many=True)

    class Meta:
        model = EtsyReceipt
        exclude = []


class DownloadEtsyReceiptSerializer(BaseEtsyReceiptSerializer):
    class Meta(BaseEtsyReceiptSerializer.Meta):
        exclude = ["marketplace_user_account"]
        extra_kwargs = {"receipt_id": {"validators": []}}

    def to_internal_value(self, data):
        # Format timestamp datetime to django datetime
        for time_key in ["creation_tsz", "last_modified_tsz"]:
            timestamp = data.pop(time_key, None)
            if timestamp:
                data[time_key] = timezone.make_aware(
                    timezone.datetime.fromtimestamp(timestamp)
                )
        return super().to_internal_value(data)

    def create(self, validated_data) -> EtsyReceipt:
        # Get filter fields
        shipping_details: dict = validated_data.pop("shipping_details")
        marketplace_user_account: str = validated_data.pop("marketplace_user_account")
        receipt_id: str = validated_data.pop("receipt_id")
        # Create or update receipt instance
        instance: EtsyReceipt
        created: bool
        instance, created = EtsyReceipt.objects.update_or_create(
            marketplace_user_account=marketplace_user_account,
            receipt_id=receipt_id,
            defaults=validated_data,
        )
        # Create or update shipping details
        if shipping_details:
            EtsyReceiptShippingDetails.objects.update_or_create(
                receipt=instance, defaults=shipping_details
            )
        # Return EtsyReceipt
        return instance
