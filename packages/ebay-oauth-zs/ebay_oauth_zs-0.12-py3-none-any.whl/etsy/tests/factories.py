import factory

from etsy.policy.models import EtsyPaymentTemplate


class EtsyCountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = EtsyPaymentTemplate
