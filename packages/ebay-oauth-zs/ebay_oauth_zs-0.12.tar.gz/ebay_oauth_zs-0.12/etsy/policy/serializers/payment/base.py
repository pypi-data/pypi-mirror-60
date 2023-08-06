from rest_framework import serializers

from etsy.policy.models import EtsyPaymentTemplate


class BaseEtsyPaymentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtsyPaymentTemplate
        fields = "__all__"
