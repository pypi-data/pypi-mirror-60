from etsy.policy.serializers.payment.update import UpdateEtsyPaymentTemplateSerializer


class RemoteUpdateEtsyPaymentTemplateSerializer(UpdateEtsyPaymentTemplateSerializer):
    class Meta(UpdateEtsyPaymentTemplateSerializer.Meta):
        fields = UpdateEtsyPaymentTemplateSerializer.Meta.fields + [
            "payment_template_id",
            "shop_id",
        ]
