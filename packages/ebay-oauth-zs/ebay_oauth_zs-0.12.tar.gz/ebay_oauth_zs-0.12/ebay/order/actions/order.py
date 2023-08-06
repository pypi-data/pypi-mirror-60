from ebay.api.ebay_action import EbayAccountAction
from ebay.listing.models import EbayListing
from ebay.order.serializers.api.order import EbayOrderSerializer
from ebay_api.sell.fulfillment import order as order_api

from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


class RemoteGetEbayOrders(EbayAccountAction):
    description = "Загрузка заказов с eBay"
    api_class = order_api.GetOrders
    next_token_action = True

    def success_trigger(self, message, objects, **kwargs):
        orders_data = {"total": 0, "orders": []}
        for order_data in objects["results"]:
            orders_data["total"] += order_data["total"]
            orders_data["orders"] += order_data["orders"]
        objects["results"] = orders_data
        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadEbayOrders(RemoteGetEbayOrders):
    description = "Загрузка и сохранение заказов с eBay"

    def success_trigger(
        self,
        message: str,
        objects: dict,
        filter_by_user_products: bool = False,
        **kwargs,
    ):
        is_success, message, objects = super().success_trigger(
            message, objects, **kwargs
        )
        user_products_query = EbayListing.objects.all()

        if filter_by_user_products:
            logger.debug(f"Товары пользователя: {list(user_products_query)}")
            if not len(user_products_query):
                return super().success_trigger(message=message, objects=objects)

        saved_orders = []
        for order in objects["results"]["orders"]:
            order.update({"marketplace_user_account": self.marketplace_user_account.id})
            if (not filter_by_user_products) or self.order_contains_local_product(
                order, user_products_query
            ):
                serializer = EbayOrderSerializer(data=order)
                if serializer.is_valid(raise_exception=True):
                    order_instance = serializer.save()
                    saved_orders.append(order_instance.id)
                    logger.debug(f'Заказ сохранён (ID: {order["orderId"]}).')
            else:
                logger.debug(
                    f'Заказ не сохранён (ID: {order["orderId"]}), так как не содержит товаров, созданных в системе.'
                )
        objects["results"]["saved_orders"] = saved_orders

        return is_success, message, objects

    def order_contains_local_product(self, order, user_products_query):
        """
        Checks if the order contains at least 1 eBay product created locally by user
        """
        line_item_skus = [
            line_item.get("sku", None)
            for line_item in order["lineItems"]
            if line_item.get("sku", None)
        ]
        return bool(len(user_products_query.filter(sku__in=line_item_skus)))
