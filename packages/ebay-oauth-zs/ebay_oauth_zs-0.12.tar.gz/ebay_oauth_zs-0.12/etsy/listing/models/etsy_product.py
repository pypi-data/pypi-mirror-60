from django.db import models

from etsy.listing.models import EtsyListing

from zonesmart.models import UUIDModel
from model_utils.models import SoftDeletableModel


class EtsyProduct(UUIDModel, SoftDeletableModel):
    listing = models.ForeignKey(
        EtsyListing,
        on_delete=models.CASCADE,
        related_name="products",
        related_query_name="product",
    )
    # Fields
    product_id = models.CharField(
        max_length=30, blank=True, null=True, unique=True, verbose_name="ID продукта",
    )
    offering_id = models.CharField(
        max_length=30, blank=True, null=True, unique=True, verbose_name="ID оффера",
    )
    sku = models.CharField(max_length=50, verbose_name="SKU")
    price = models.FloatField(verbose_name="Цена (USD)")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество",)
    is_enabled = models.BooleanField(
        blank=True, default=False, verbose_name="Товар доступен",
    )

    def __str__(self):
        return f"Вариация листинга (SKU: {self.sku})"
