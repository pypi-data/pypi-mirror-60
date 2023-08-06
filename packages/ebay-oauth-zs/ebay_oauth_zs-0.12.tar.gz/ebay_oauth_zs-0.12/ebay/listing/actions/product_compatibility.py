from ebay.api.ebay_action import EbayAction
from ebay.listing.serializers.listing.compatibility.base import (
    BaseEbayProductCompatibilitySerializer,
)
from ebay_api.commerce.compatibility import (
    GetCompatibilityProperties,
    GetCompatibilityPropertyValues,
)
from ebay_api.sell.inventory import item as compatibility_api

from .base import EbayListingAction


class RemoteCreateCompatibleProducts(EbayListingAction):
    description = "Загрузка на eBay информации о совместимом с товаром транспорте"
    api_class = compatibility_api.CreateOrReplaceProductCompatibility
    payload_serializer = BaseEbayProductCompatibilitySerializer


class GetCompatibleProducts(EbayListingAction):
    description = "Получение информации о совместимом с товаром транспорте с eBay"
    api_class = compatibility_api.GetProductCompatibility


class RemoteDownloadCompatibleProducts(EbayListingAction):
    description = (
        "Получение и сохранение информации о совместимом с товаром транспорте с eBay"
    )

    def success_trigger(self, message, objects, **kwargs):
        # TODO
        return super().success_trigger(message, objects, **kwargs)


class RemoteDeleteCompatibleProducts(EbayListingAction):
    description = "Удаление информации о совместимом с товаром транспорте с eBay"
    api_class = compatibility_api.DeleteProductCompatibility


class GetProductCompatibilityProperties(EbayAction):
    description = "Получение названий аспектов совместимого с товаром транспорта"
    api_class = GetCompatibilityProperties

    def success_trigger(self, message, objects, **kwargs):
        objects["results"] = objects["results"]["compatibilityProperties"]
        return super().success_trigger(message, objects, **kwargs)


class GetCompatibilityPropertyValues(EbayAction):
    description = (
        "Получение возможных значений аспекта совместимого с товаром транспорта"
    )
    api_class = GetCompatibilityPropertyValues

    def get_query_params(self, **kwargs):
        kwargs["filter"] = kwargs.pop("filter_query", None)
        return super().get_query_params(**kwargs)

    def success_trigger(self, message, objects, **kwargs):
        if objects["response"].status_code == 204:
            message = (
                "Ошибка при попытке получить возможные значения аспекта.\n"
                f'Неверно заданы параметры фильтра: filter="{self.query_params.get("filter", "None")}".'
            )
            return super().failure_trigger(message, objects)

        objects["results"] = [
            item["value"] for item in objects["results"]["compatibilityPropertyValues"]
        ]
        return super().success_trigger(message, objects, **kwargs)
