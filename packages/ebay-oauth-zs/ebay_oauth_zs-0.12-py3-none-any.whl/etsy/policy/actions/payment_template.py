from etsy.api.etsy_action import EtsyAccountAction, EtsyEntityAction
from etsy.api.etsy_api.actions.policy import (
    GetEtsyPaymentTemplateList,
    UpdateEtsyPaymentTemplate,
)
from etsy.policy.models import EtsyPaymentTemplate
from etsy.policy.serializers.payment.remote import (
    RemoteDownloadEtsyPaymentTemplateSerializer,
    RemoteUpdateEtsyPaymentTemplateSerializer,
)


class RemoteGetEtsyPaymentTemplateList(EtsyAccountAction):
    api_class = GetEtsyPaymentTemplateList


class RemoteDownloadEtsyPaymentTemplateList(RemoteGetEtsyPaymentTemplateList):
    def success_trigger(self, message: str, objects: dict, **kwargs):
        serializer = RemoteDownloadEtsyPaymentTemplateSerializer(
            data=objects["results"][0]
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(channel=self.channel)
        return super().success_trigger(message, objects, **kwargs)


class RemoteUpdateEtsyPaymentTemplate(EtsyEntityAction):  # always server error
    entity_model = EtsyPaymentTemplate
    entity_name = "payment_template"
    api_class = UpdateEtsyPaymentTemplate

    def get_params(self, **kwargs):
        kwargs.update(
            RemoteUpdateEtsyPaymentTemplateSerializer(self.payment_template).data
        )
        return super().get_params(**kwargs)
