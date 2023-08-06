from django.contrib import admin

import nested_admin
from ebay.order import models


@admin.register(models.EbayOrder)
class EbayOrderAdmin(nested_admin.NestedModelAdmin):

    verbose_name = "Заказ eBay"
    verbose_name_plural = "Заказы с eBay"
    list_display = [
        "sellerId",
        "orderId",
        "buyer_username",
        "orderFulfillmentStatus",
        "orderPaymentStatus",
        "creationDate",
        "lastModifiedDate",
    ]
    list_filter = ["orderFulfillmentStatus", "orderPaymentStatus"]
    exclude = []
    inlines = []


@admin.register(models.EbayOrderLineItem)
class LineItemAdmin(nested_admin.NestedModelAdmin):

    verbose_name = "Товар из заказа"
    verbose_name_plural = "Товары из заказа"
    list_display = [
        "order",
        "sku",
        "quantity",
        "lineItemId",
        "lineItemFulfillmentStatus",
        "soldFormat",
    ]
    list_filter = ["lineItemFulfillmentStatus", "soldFormat"]
    exclude = []
    inlines = []
