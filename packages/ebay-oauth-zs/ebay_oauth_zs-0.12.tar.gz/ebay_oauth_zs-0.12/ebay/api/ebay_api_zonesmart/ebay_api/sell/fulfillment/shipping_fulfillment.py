from .order import OrderAPI


class ShippingFulfillmentAPI(OrderAPI):
    required_path_params = ["orderId"]
    url_postfix = "shipping_fulfillment"


class CreateShippingFulfillment(ShippingFulfillmentAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/fulfillment/resources/order/shipping_fulfillment/methods/createShippingFulfillment
    """

    method_type = "POST"


class GetShippingFulfillment(ShippingFulfillmentAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/fulfillment/resources/order/shipping_fulfillment/methods/getShippingFulfillment
    """

    method_type = "GET"
    required_path_params = ["orderId", "fulfillmentId"]


class GetShippingFulfillments(ShippingFulfillmentAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/fulfillment/resources/order/shipping_fulfillment/methods/getShippingFulfillments
    """

    method_type = "GET"
