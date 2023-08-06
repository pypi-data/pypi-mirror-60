from etsy.api.etsy_action import EtsyAccountAction
from etsy.api.etsy_api.actions.policy import (
    CreateEtsyShippingTemplateEntry,
    GetEtsyShippingTemplateEntryList,
    GetEtsyShippingTemplateEntry,
    UpdateEtsyShippingTemplateEntry,
    DeleteEtsyShippingTemplateEntry,
)


class RemoteCreateEtsyShippingTemplateEntry(EtsyAccountAction):
    api_class = CreateEtsyShippingTemplateEntry


class RemoteGetEtsyShippingTemplateEntryList(EtsyAccountAction):
    api_class = GetEtsyShippingTemplateEntryList


class RemoteGetEtsyShippingTemplateEntry(EtsyAccountAction):
    api_class = GetEtsyShippingTemplateEntry


class RemoteUpdateEtsyShippingTemplateEntry(EtsyAccountAction):
    api_class = UpdateEtsyShippingTemplateEntry


class RemoteDeleteEtsyShippingTemplateEntry(EtsyAccountAction):
    api_class = DeleteEtsyShippingTemplateEntry
