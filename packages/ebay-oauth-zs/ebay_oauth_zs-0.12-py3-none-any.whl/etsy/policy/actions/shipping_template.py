from typing import Tuple

from etsy.api.etsy_action import EtsyAccountAction, EtsyEntityAction
from etsy.policy.models import EtsyShippingTemplate
from etsy.policy.serializers.shipping.remote.upload import (
    RemoteCreateEtsyShippingTemplateSerializer,
)
from etsy.policy.serializers.shipping.remote.download import (
    RemoteDownloadEtsyShippingTemplateSerializer,
)
from etsy.policy.actions.shipping_template_entry import (
    RemoteCreateEtsyShippingTemplateEntry,
    RemoteGetEtsyShippingTemplateEntryList,
)
from etsy.api.etsy_api.actions.policy import (
    GetEtsyShippingTemplateList,
    GetEtsyShippingTemplate,
    DeleteEtsyShippingTemplate,
    CreateEtsyShippingTemplate,
    UpdateEtsyShippingTemplate,
)


class RemoteGetEtsyShippingTemplate(EtsyAccountAction):
    api_class = GetEtsyShippingTemplate


class RemoteGetEtsyShippingTemplateList(EtsyAccountAction):
    api_class = GetEtsyShippingTemplateList


class EtsyShippingTemplateAction(EtsyEntityAction):
    entity_model = EtsyShippingTemplate
    entity_name = "shipping_template"

    def get_params(self, **kwargs):
        if getattr(self.shipping_template, "shipping_template_id", None):
            kwargs["shipping_template_id"] = self.shipping_template.shipping_template_id
        return super().get_params(**kwargs)


class RemoteCreateEtsyShippingTemplate(EtsyShippingTemplateAction):
    api_class = CreateEtsyShippingTemplate
    publish_final_status = True

    def success_trigger(self, message, objects, **kwargs):
        self.shipping_template.shipping_template_id = objects["results"][0][
            "shipping_template_id"
        ]
        self.shipping_template.save()
        return super().success_trigger(message, objects, **kwargs)


class RemoteUpdateEtsyShippingTemplate(EtsyShippingTemplateAction):
    api_class = UpdateEtsyShippingTemplate
    publish_final_status = True


class RemoteDeleteEtsyShippingTemplate(EtsyShippingTemplateAction):
    api_class = DeleteEtsyShippingTemplate
    publish_final_status = False


class SyncEtsyShippingTemplateAndEntryList(EtsyShippingTemplateAction):
    def create_template(self, template_data: dict):
        return self.raisable_action(RemoteCreateEtsyShippingTemplate, **template_data,)

    def update_template(self, template_data: dict):
        return self.raisable_action(RemoteUpdateEtsyShippingTemplate, **template_data,)

    def create_or_update_entry(self, entry_data: dict):
        return self.raisable_action(
            RemoteCreateEtsyShippingTemplateEntry, **entry_data,
        )

    def make_request(self, **kwargs):
        data = RemoteCreateEtsyShippingTemplateSerializer(self.shipping_template).data

        try:
            # create or update shipping template on Etsy
            if self.shipping_template.published:
                # case: shipping template is already uploaded
                entries_data = data.pop("entries")
                template_data = data
                self.update_template(template_data)
            else:
                # case: shipping template is not uploaded
                entries_data = data.pop("entries")
                template_data = {**data, **entries_data[0]}
                entries_data = entries_data[1:]
                self.create_template(template_data)

            # sync entries
            for entry_data in entries_data:
                # TODO: delete if is_removed == True
                entry_data.update(
                    {
                        "shipping_template_id": self.shipping_template.shipping_template_id
                    }
                )
                self.create_or_update_entry(entry_data)

        except self.exception_class as error:
            is_success = False
            message = (
                "Не удалось синхронизировать политику доставки с Etsy "
                f"(название: {self.shipping_template.title[:30]}).\n{error}"
            )
            objects = {"response": getattr(error, "response", None)}

        else:
            is_success = True
            message = (
                "Политика доставки успешно синхронизирована с Etsy "
                f"(название: {self.shipping_template.title[:30]})."
            )
            objects = {
                "shipping_template_id": self.shipping_template.shipping_template_id
            }

        return is_success, message, objects


class RemoteDownloadEtsyShippingTemplateList(RemoteGetEtsyShippingTemplateList):
    def get_shipping_template_entries(
        self, shipping_template_id
    ) -> Tuple[bool, str, dict]:
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyShippingTemplateEntryList,
            shipping_template_id=shipping_template_id,
        )
        return objects["results"]

    def success_trigger(self, message: str, objects: dict, **kwargs):
        # Get shipping template entries for each shipping template
        for shipping_template in objects["results"]:
            entries = self.get_shipping_template_entries(
                shipping_template["shipping_template_id"]
            )
            # Format entries
            for entry in entries:
                entry["destination_country"] = entry.pop("destination_country_id", None)
                entry["destination_region"] = entry.pop("destination_region_id", None)
            # Add entries for shipping template
            shipping_template["entries"] = entries
        # Validate shipping templates data
        serializer = RemoteDownloadEtsyShippingTemplateSerializer(
            data=objects["results"], many=True
        )
        serializer.is_valid(raise_exception=True)
        # Save shipping templates
        serializer.save(marketplace_user_account=self.marketplace_user_account)
        return True, "Политики доставки успешно загружены.", {}
