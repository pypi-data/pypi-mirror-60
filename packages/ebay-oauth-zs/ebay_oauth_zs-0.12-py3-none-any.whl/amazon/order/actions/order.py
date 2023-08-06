import datetime

from amazon.api.amazon_action import AmazonOrderAction
from amazon.order.serializers.order import BaseAmazonOrderSerializer
from amazon.utils import jsonify_object_dict


class GetAmazonOrders(AmazonOrderAction):
    def make_request(self, **query_params):
        amazon_order_ids = query_params.pop("amazon_order_ids", None)
        if amazon_order_ids:
            is_success, message, objects = self.api.get_orders(amazon_order_ids)
        else:
            if not query_params.get("marketplace_ids", None):
                query_params["marketplace_ids"] = [self.marketplace_id]

            if (not query_params.get("created_after", None)) and (
                not query_params.get("last_updated_after", None)
            ):
                query_params["created_after"] = datetime.datetime(
                    2000, 1, 1, 0, 0, 0, 0
                ).isoformat()

            is_success, message, objects = self.api.list_orders(**query_params)

        if is_success:
            message = f"Заказы Amazon успешно загружены."
            objects["results"] = jsonify_object_dict(
                objects["response"].parsed["Orders"]["Order"]
            )
        else:
            message = f"Не удалось загрузить заказы Amazon.\n{message}"

        return is_success, message, objects


class DownloadAmazonOrders(GetAmazonOrders):
    def success_trigger(self, message: str, objects: dict, **kwargs):
        order_list = objects["results"]
        for order in order_list:
            payment_method_details = order.get("PaymentMethodDetails", None)
            # Create list with 1 method if len is equals 1
            if payment_method_details and len(payment_method_details) == 1:
                order["PaymentMethodDetails"] = [payment_method_details]
            order["channel"] = self.channel.id

        serializer = BaseAmazonOrderSerializer(data=order_list, many=True)
        if serializer.is_valid():
            is_success = True
            message = "Заказы Amazon успешно загружены и сохранены."
            serializer.save()
        else:
            is_success = False
            message = (
                "Не удалось сохранить загруженные заказы Amazon.\n"
                f"Ошибки:\n{serializer.errors}"
            )
        return is_success, message, objects
