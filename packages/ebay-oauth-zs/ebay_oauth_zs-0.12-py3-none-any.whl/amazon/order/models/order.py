# docs: http://docs.developer.amazonservices.com/en_IN/orders-2013-09-01/Orders_Datatypes.html#Order
import json

from django.db import models

from zonesmart.marketplace.models import Channel
from zonesmart.models import UUIDModel


class AmazonOrder(UUIDModel):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="amazon_orders",
        related_query_name="amazon_order",
        limit_choices_to={
            "domain__marketplace__unique_name__in": [
                "amazon_north_america",
                "amazon_europe",
                "amazon_far_east",
            ],
        },
    )
    MarketplaceId = models.CharField(max_length=30, blank=True, null=True)
    SalesChannel = models.CharField(max_length=30, blank=True, null=True)
    FulfillmentChannel = models.CharField(max_length=30, blank=True, null=True)
    OrderChannel = models.CharField(max_length=30, blank=True, null=True)

    AmazonOrderId = models.CharField(max_length=30)
    SellerOrderId = models.CharField(max_length=30, blank=True, default="")
    OrderStatus = models.CharField(max_length=30)
    OrderType = models.CharField(max_length=30, blank=True, null=True)

    PurchaseDate = models.DateTimeField()
    LastUpdateDate = models.DateTimeField()
    LatestShipDate = models.DateTimeField(blank=True, null=True)
    LatestDeliveryDate = models.DateTimeField(blank=True, null=True)
    EarliestDeliveryDate = models.DateTimeField(blank=True, null=True)

    BuyerName = models.CharField(max_length=50, blank=True, null=True)
    BuyerEmail = models.EmailField(blank=True, null=True)

    IsReplacementOrder = models.BooleanField(blank=True, null=True)
    IsBusinessOrder = models.BooleanField(blank=True, null=True)
    IsPremiumOrder = models.BooleanField(blank=True, null=True)
    IsPrime = models.BooleanField(blank=True, null=True)

    NumberOfItemsShipped = models.PositiveSmallIntegerField(blank=True, null=True)
    NumberOfItemsUnshipped = models.PositiveSmallIntegerField(blank=True, null=True)

    ShipServiceLevel = models.CharField(max_length=30, blank=True, null=True)
    ShipmentServiceLevelCategory = models.CharField(
        max_length=30, blank=True, null=True
    )

    PaymentMethod = models.CharField(max_length=30, blank=True, null=True)
    _payment_method_details = models.TextField(default="[]")

    PurchaseOrderNumber = models.CharField(max_length=50, blank=True, null=True)

    # buyer_tax_info
    CompanyLegalName = models.CharField(max_length=100, blank=True, null=True)
    TaxingRegion = models.CharField(max_length=50, blank=True, null=True)
    # + tax_classifications

    # order total
    OrderTotalCurrencyCode = models.CharField(max_length=3, blank=True, null=True)
    OrderTotalAmount = models.FloatField(blank=True, null=True)

    IsAddressSharingConfidential = models.BooleanField(blank=True, null=True)

    @property
    def payment_method_details(self):
        return json.loads(self._payment_method_details)

    @payment_method_details.setter
    def payment_method_details(self, value):
        self._payment_method_details = json.dumps(
            list(self.payment_method_details + value)
        )

    def __str__(self):
        return f"Заказ Amazon (ID: {self.AmazonOrderId})"

    class Meta:
        verbose_name = "Заказ Amazon"
        verbose_name_plural = "Заказы Amazon"


class TaxClassification(models.Model):
    order = models.ForeignKey(
        AmazonOrder, on_delete=models.CASCADE, related_name="tax_classifications"
    )
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)


class AmazonShippingAddress(UUIDModel):
    order = models.OneToOneField(
        AmazonOrder, on_delete=models.CASCADE, related_name="shipping_address"
    )
    Name = models.CharField(max_length=50, blank=True, verbose_name="Имя")
    CountryCode = models.CharField(max_length=2, blank=True, default="")
    StateOrRegion = models.CharField(max_length=50, blank=True, default="")
    County = models.CharField(max_length=50, blank=True, default="")
    City = models.CharField(max_length=50, blank=True, default="")
    AddressLine1 = models.CharField(max_length=100, blank=True, default="")
    AddressLine2 = models.CharField(max_length=100, blank=True, default="")
    AddressLine3 = models.CharField(max_length=100, blank=True, default="")
    PostalCode = models.CharField(max_length=30, blank=True, default="")
    Phone = models.CharField(max_length=20, blank=True, null=True)
    AddressType = models.CharField(max_length=20, blank=True, null=True)
