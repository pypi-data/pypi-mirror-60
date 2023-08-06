from rest_framework import serializers
from django.utils import timezone

from etsy.order.models.transaction import EtsyReceiptTransaction


class BaseReceiptTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyReceiptTransaction
        exclude = ["receipt"]


class RemoteDownloadReceiptTransactionSerializer(BaseReceiptTransactionSerializer):
    class Meta(BaseReceiptTransactionSerializer.Meta):
        extra_kwargs = {"transaction_id": {"validators": []}}

    def to_internal_value(self, data):
        for time_key in ["creation_tsz", "paid_tsz", "shipped_tsz"]:
            timestamp = data.pop(time_key, None)
            if timestamp:
                data[time_key] = timezone.make_aware(
                    timezone.datetime.fromtimestamp(timestamp)
                )
        return super().to_internal_value(data)

    def create(self, validated_data):
        receipt = validated_data.pop("receipt")
        transaction_id = validated_data.pop("transaction_id")
        instance, created = self.Meta.model.objects.update_or_create(
            receipt=receipt, transaction_id=transaction_id, defaults=validated_data
        )
        return instance
