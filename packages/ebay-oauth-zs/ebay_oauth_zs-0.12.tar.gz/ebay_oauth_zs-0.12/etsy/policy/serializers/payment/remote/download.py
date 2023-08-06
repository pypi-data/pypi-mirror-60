from etsy.policy.serializers.payment.base import BaseEtsyPaymentTemplateSerializer


class RemoteDownloadEtsyPaymentTemplateSerializer(BaseEtsyPaymentTemplateSerializer):
    class Meta:
        model = BaseEtsyPaymentTemplateSerializer.Meta.model
        exclude = ["channel"]

    def create(self, validated_data):
        payment_template_id = validated_data.pop("payment_template_id")
        instance, created = self.Meta.model.objects.update_or_create(
            payment_template_id=payment_template_id, defaults=validated_data
        )
        return instance
