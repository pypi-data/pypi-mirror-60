from ebay.data import enums
from ebay.policy import models
from ebay.policy.serializers import (
    AbstractCategoryTypeSerializer,
    AbstractPolicySerializer,
)
from rest_framework import serializers


class AbstractPaymentMethodSerializer(serializers.ModelSerializer):
    brands = serializers.MultipleChoiceField(
        choices=enums.PaymentInstrumentBrandEnum, required=False
    )

    class Meta:
        model = models.AbstractPaymentMethod
        abstract = True

    def validate(self, attrs):
        payment_method_type = attrs.get("paymentMethodType")
        if payment_method_type:
            if payment_method_type == "CREDIT_CARD" and not attrs.get("brands"):
                raise serializers.ValidationError(
                    {
                        "brands": "This fields is required if paymentMethodType is set to CREDIT_CARD."
                    },
                    code="required",
                )
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["brands"] = list(representation["brands"])
        return representation


class BaseRecipientAccountReference(serializers.ModelSerializer):
    class Meta:
        model = models.RecipientAccountReference
        exclude = ["id", "payment_method"]


class BasePaymentMethodSerializer(AbstractPaymentMethodSerializer):
    recipientAccountReference = BaseRecipientAccountReference(required=False)

    class Meta:
        model = models.PaymentMethod
        exclude = ["id", "payment_policy"]


class BaseFullPaymentDueInSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FullPaymentDueIn
        exclude = ["id", "payment_policy"]


class BaseDepositRecipientAccountReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DepositRecipientAccountReference
        exclude = ["id", "deposit_payment_method"]


class BaseDepositPaymentMethodSerializer(AbstractPaymentMethodSerializer):
    recipientAccountReference = BaseDepositRecipientAccountReferenceSerializer(
        required=False
    )

    class Meta:
        model = models.DepositPaymentMethod
        exclude = ["id", "deposit"]


class BaseDepositDueInSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DepositDueIn
        exclude = ["id", "deposit"]


class BaseDepositAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DepositAmount
        exclude = ["id", "deposit"]


class BasePaymentPolicyDepositSerializer(serializers.ModelSerializer):
    amount = BaseDepositAmountSerializer(required=False)
    dueIn = BaseDepositDueInSerializer(required=False)
    paymentMethods = BaseDepositPaymentMethodSerializer(required=False, many=True)

    class Meta:
        model = models.Deposit
        exclude = [
            "id",
            "payment_policy",
        ]


class BasePaymentPolicyCategoryTypeSerializer(AbstractCategoryTypeSerializer):
    class Meta(AbstractCategoryTypeSerializer.Meta):
        model = models.PaymentPolicyCategoryType


class BasePaymentPolicySerializer(AbstractPolicySerializer):
    categoryTypes = BasePaymentPolicyCategoryTypeSerializer(
        many=True, allow_empty=False, required=False
    )
    deposit = BasePaymentPolicyDepositSerializer(required=False)
    fullPaymentDueIn = BaseFullPaymentDueInSerializer(required=False)
    paymentMethods = BasePaymentMethodSerializer(required=False, many=True)

    class Meta(AbstractPolicySerializer.Meta):
        model = models.PaymentPolicy
        fields = AbstractPolicySerializer.Meta.fields + [
            "immediatePay",
            "paymentInstructions",
            "deposit",
            "fullPaymentDueIn",
            "paymentMethods",
        ]

    def validate(self, attrs):
        if attrs.get("deposit"):
            category_types = attrs.get("categoryTypes")
            if "MOTORS_VEHICLES" not in [
                category_type["name"] for category_type in category_types
            ]:
                raise serializers.ValidationError(
                    {
                        "deposit": "This container is applicable only "
                        "if the categoryTypes.name field is set to MOTORS_VEHICLES."
                    }
                )
        return attrs
