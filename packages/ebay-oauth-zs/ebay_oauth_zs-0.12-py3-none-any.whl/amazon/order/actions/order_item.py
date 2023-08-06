from amazon.api.amazon_action import AmazonOrderAction
from amazon.order.models import AmazonOrder
from amazon.order.serializers.order_item import CreateAmazonOrderItemSerializer
from amazon.utils import jsonify_object_dict


class GetAmazonOrderItems(AmazonOrderAction):
    def make_request(self, order_id=None, amazon_order_id=None):
        if not amazon_order_id:
            if not order_id:
                raise AttributeError(
                    'Необходимо задать "order_id" или "amazon_order_id".'
                )
            order = AmazonOrder.objects.get(id=order_id)
            amazon_order_id = order.AmazonOrderId

        is_success, message, objects = self.api.list_order_items(amazon_order_id)
        if is_success:
            order_items = objects["response"].parsed["OrderItems"]["OrderItem"]
            if not isinstance(order_items, list):
                order_items = [order_items]

            message = f"Товары из заказа Amazon успешно загружены (ID: amazon_order_id).\n{message}"
            objects["results"] = jsonify_object_dict(order_items)
        else:
            message = f"Не удалось загрузить товары из заказа Amazon (ID: amazon_order_id).\n{message}"
        return is_success, message, objects


class DownloadAmazonOrderItems(GetAmazonOrderItems):
    def success_trigger(self, message: str, objects: dict, **kwargs):
        # TODO: rework action call & success call trigger & add entity (order)
        objects = objects["results"]
        order_items = objects["order_items"]
        order_id = objects["order_id"]
        for order_item in order_items:
            order_item["order"] = order_id
        serializer = CreateAmazonOrderItemSerializer(
            data=objects["order_items"], many=True
        )
        if serializer.is_valid():
            is_success = True
            message = (
                "Товары из заказа Amazon успешно загружены и сохранены (ID: order_id)."
            )
            serializer.save()
        else:
            is_success = False
            message = (
                "Не удалось сохранить загруженные товары заказа Amazon (ID: order_id).\n"
                f"Ошибки:\n{serializer.errors}"
            )
        return is_success, message, objects
