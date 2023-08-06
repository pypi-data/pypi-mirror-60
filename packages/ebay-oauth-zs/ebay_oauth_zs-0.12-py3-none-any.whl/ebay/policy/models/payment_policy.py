from django.core import validators
from django.db import models

from ebay.policy.models import (
    AbstractCategoryType,
    AbstractPaymentMethod,
    AbstractPolicy,
    AbstractPolicyAmount,
    AbstractRecipientAccountReference,
    AbstractTimeDuration,
)
from model_utils import Choices, FieldTracker

from zonesmart.marketplace.models import Channel
from zonesmart.models import NestedUpdateOrCreateModelManager, UUIDModel


class PaymentPolicy(AbstractPolicy):
    REQUIRED_FOR_PUBLISHING_FIELDS = AbstractPolicy.REQUIRED_FOR_PUBLISHING_FIELDS + [
        "categoryTypes",
        "paymentMethods",
    ]
    # Tracker should be added for each model that requires fields update tracking
    # https://github.com/jazzband/django-model-utils/issues/155
    tracker = FieldTracker()
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        limit_choices_to={"domain__marketplace__unique_name": "ebay"},
        related_name="payment_policies",
        related_query_name="payment_policy",
        verbose_name="Channel",
    )
    immediatePay = models.BooleanField(default=False, verbose_name="Immediate pay")
    paymentInstructions = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name="Payment instructions"
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Политика оплаты"
        verbose_name_plural = "Политики оплаты"
        default_related_name = "payment_policy"


class PaymentPolicyCategoryType(AbstractCategoryType):
    payment_policy = models.ForeignKey(
        PaymentPolicy,
        on_delete=models.CASCADE,
        related_name="categoryTypes",
        verbose_name="Payment policy",
    )

    class Meta:
        verbose_name = "Payment policy category type"


# This container is applicable only if the categoryTypes.name field is set to MOTORS_VEHICLES.
# https://developer.ebay.com/api-docs/sell/account/resources/payment_policy/methods/getPaymentPolicy#response.deposit
class Deposit(UUIDModel):
    payment_policy = models.OneToOneField(
        PaymentPolicy,
        on_delete=models.CASCADE,
        related_name="deposit",
        verbose_name="Payment policy",
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Payment policy deposit"


class DepositAmount(AbstractPolicyAmount):
    deposit = models.OneToOneField(
        Deposit, on_delete=models.CASCADE, related_name="amount", verbose_name="Deposit"
    )
    value = models.FloatField(
        default=0.0,
        validators=[
            validators.MinValueValidator(0.0),
            validators.MaxValueValidator(2000.0),
        ],
        verbose_name="Value",
    )

    class Meta:
        verbose_name = "Deposit amount"


class DepositDueIn(AbstractTimeDuration):
    deposit = models.OneToOneField(
        Deposit, on_delete=models.CASCADE, related_name="dueIn", verbose_name="Deposit"
    )
    unit = models.CharField(
        max_length=4, editable=False, default="HOUR", verbose_name="Unit"
    )
    value = models.PositiveIntegerField(
        default=48,
        validators=[validators.MinValueValidator(24), validators.MaxValueValidator(72)],
        verbose_name="Value",
        help_text="Min=24 (hours), Max=72 (hours), Default=48 (hours)",
    )

    class Meta:
        verbose_name = "Deposit due in"


class DepositPaymentMethod(AbstractPaymentMethod):
    deposit = models.ForeignKey(
        Deposit,
        on_delete=models.CASCADE,
        related_name="paymentMethods",
        verbose_name="Deposit",
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Deposit payment method"


class DepositRecipientAccountReference(AbstractRecipientAccountReference):
    deposit_payment_method = models.OneToOneField(
        DepositPaymentMethod,
        on_delete=models.CASCADE,
        related_name="recipientAccountReference",
        verbose_name="Deposit payment method",
    )

    class Meta:
        verbose_name = "Deposit recipient account reference"


class FullPaymentDueIn(AbstractTimeDuration):
    VALUE_CHOICES = Choices(
        (3, "three", "3"), (7, "seven", "7"), (10, "ten", "10"), (14, "fourteen", "14"),
    )
    payment_policy = models.OneToOneField(
        PaymentPolicy,
        on_delete=models.CASCADE,
        related_name="fullPaymentDueIn",
        verbose_name="Payment policy",
    )
    unit = models.CharField(
        max_length=3, editable=False, default="DAY", verbose_name="Unit"
    )
    value = models.PositiveIntegerField(
        default=VALUE_CHOICES.seven, choices=VALUE_CHOICES, verbose_name="Value",
    )


class PaymentMethod(AbstractPaymentMethod):
    payment_policy = models.ForeignKey(
        PaymentPolicy,
        on_delete=models.CASCADE,
        related_name="paymentMethods",
        verbose_name="Payment policy",
    )

    objects = NestedUpdateOrCreateModelManager()

    class Meta:
        verbose_name = "Payment policy payment method"


class RecipientAccountReference(AbstractRecipientAccountReference):
    payment_method = models.OneToOneField(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name="recipientAccountReference",
    )
