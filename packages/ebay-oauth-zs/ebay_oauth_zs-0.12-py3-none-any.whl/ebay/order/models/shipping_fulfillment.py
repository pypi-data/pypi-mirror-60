from django.db import models

from ebay.data.enums.shipping_carriers_enum import ShippingCarriersEnum
from ebay.order.models import EbayOrder, EbayOrderLineItem

from zonesmart.marketplace.models import MarketplaceEntity
from zonesmart.models import UUIDModel


class EbayShippingFulfillment(MarketplaceEntity):
    order = models.ForeignKey(
        EbayOrder,
        on_delete=models.CASCADE,
        related_name="shipping_fulfillments",
        related_query_name="shipping_fulfillment",
        verbose_name="Заказ eBay",
    )
    fulfillmentId = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="ID фулфилмента",
    )
    shippedDate = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата и время отправки",
    )
    shippingCarrierCode = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        choices=ShippingCarriersEnum,
        verbose_name="Курьерская служба",
    )
    shippingServiceCode = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Курьерская служба",
    )
    shipmentTrackingNumber = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Трекинговый номер"
    )

    @property
    def published(self):
        return (self.status == self.STATUS.published) and self.fulfillmentId


class EbayShippingFulfillmentLineItem(UUIDModel):
    shipping_fulfillment = models.ForeignKey(
        EbayShippingFulfillment,
        on_delete=models.CASCADE,
        related_name="line_items",
        related_query_name="line_items",
        verbose_name="Товары из фулфилмента",
    )
    line_item = models.ForeignKey(
        EbayOrderLineItem, on_delete=models.CASCADE, verbose_name="Товар из заказа",
    )
