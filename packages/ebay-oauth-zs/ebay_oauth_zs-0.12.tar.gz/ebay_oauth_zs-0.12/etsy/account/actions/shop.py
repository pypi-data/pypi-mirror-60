from rest_framework.exceptions import ValidationError

from etsy.account.models import EtsyShop, EtsyShopSection
from etsy.account.serializers.shop.base import (
    EtsyShopSectionSerializer,
    BaseEtsyShopSerializer,
)
from etsy.api.etsy_action import EtsyAccountAction
from etsy.api.etsy_api.actions.account import GetEtsyShopList, GetEtsyShopSectionList


class RemoteGetEtsyShopList(EtsyAccountAction):
    api_class = GetEtsyShopList


class RemoteGetEtsyShopSectionList(EtsyAccountAction):
    api_class = GetEtsyShopSectionList


class RemoteGetEtsyShopsAndSections(EtsyAccountAction):
    def get_shops(self):
        is_success, message, objects = self.raisable_action(RemoteGetEtsyShopList)
        return objects["results"]

    def get_shop_sections(self, shop_id: int):
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyShopSectionList, shop_id=shop_id
        )
        return objects["results"]

    def make_request(self, **kwargs):
        # get shop data
        shop_data_list = self.get_shops()
        assert len(shop_data_list) == 1, "WTF: more than 1 shop!"
        shop_data = shop_data_list[0]
        # get shop sections data
        shop_sections_data = self.get_shop_sections(shop_id=shop_data["shop_id"])

        message = "Данные о магазине Etsy и его секциях успешно получены."
        objects = {"results": {**shop_data, "sections": shop_sections_data}}
        return True, message, objects


class RemoteDownloadEtsyShopsAndSections(RemoteGetEtsyShopsAndSections):
    def save_shop_and_sections(self, data):
        section_data_list = data.pop("sections")

        try:
            instance = EtsyShop.objects.get(shop_id=data["shop_id"])
        except EtsyShop.DoesNotExist:
            instance = None
        serializer = BaseEtsyShopSerializer(instance=instance, data=data)
        if serializer.is_valid(raise_exception=True):
            shop = serializer.save(channel=self.channel)

        for section_data in section_data_list:
            try:
                instance = EtsyShopSection.objects.get(
                    shop_section_id=section_data["shop_section_id"]
                )
            except EtsyShopSection.DoesNotExist:
                instance = None

            serializer = EtsyShopSectionSerializer(instance=instance, data=section_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(shop=shop)

    def success_trigger(self, message, objects, **kwargs):
        try:
            self.save_shop_and_sections(data=objects["results"])
        except ValidationError as error:
            return super().failure_trigger(message=str(error), objects=error, **kwargs)

        return super().success_trigger(message, objects, **kwargs)
