from django_filters import filterset
from ebay.policy.models import FulfillmentPolicy, PaymentPolicy, ReturnPolicy


class BasePolicyFilterSet(filterset.FilterSet):
    class Meta:
        model = None
        fields = ["channel"]


class FulfillmentPolicyFilterSet(BasePolicyFilterSet):
    class Meta(BasePolicyFilterSet.Meta):
        model = FulfillmentPolicy


class PaymentPolicyFilterSet(BasePolicyFilterSet):
    class Meta(BasePolicyFilterSet.Meta):
        model = PaymentPolicy


class ReturnPolicyFilterSet(BasePolicyFilterSet):
    class Meta(BasePolicyFilterSet.Meta):
        model = ReturnPolicy
