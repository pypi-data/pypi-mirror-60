from django.db import models

from ebay.data import enums
from ebay.listing.models import AbstractEbayAspect, EbayListing

from zonesmart.models import NestedUpdateOrCreateModelManager
from zonesmart.product.models import AbstractProduct


class EbayProductQuerySet(models.QuerySet):
    def all(self):
        return super().filter(is_removed=False)

    def soft_deleted(self):
        return super().filter(is_removed=True)

    def soft_deleted_values(self):
        return self.soft_deleted().values_list("sku", "offerId", named=True)

    def delete(self):
        for obj in self:
            if obj.is_removed:
                obj.delete()
            else:
                obj.is_removed = True
                obj.save()


class EbayProductManager(NestedUpdateOrCreateModelManager):
    RELATED_OBJECT_NAMES = ["specifications"]
    UPDATE_OR_CREATE_FILTER_FIELDS = {"specifications": ["name"]}

    def get_queryset(self):
        return EbayProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().all()

    def soft_deleted(self, values=False):
        qs = self.get_queryset()
        return qs.soft_deleted_values() if values else qs.soft_deleted()


class EbayProduct(AbstractProduct):
    EXTRA_IMAGES_LIMIT = 11
    listing = models.ForeignKey(
        EbayListing, on_delete=models.CASCADE, related_name="products"
    )
    # ID
    offerId = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="ID оффера в системе eBay"
    )
    listingId = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="ID листинга в системе eBay"
    )
    # Fields
    condition = models.CharField(
        max_length=30,
        default=enums.ConditionEnum.NEW,
        choices=enums.ConditionEnum,
        verbose_name="Condition",
    )
    conditionDescription = models.TextField(
        max_length=1000, blank=True, null=True, verbose_name="Condition description"
    )
    epid = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="The eBay Product Identifier (ePID)",
    )
    format_type = models.CharField(
        max_length=20,
        blank=True,
        default=enums.FormatTypeEnum.FIXED_PRICE,
        choices=enums.FormatTypeEnum,
        verbose_name="Format type",
    )
    quantityLimitPerBuyer = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name="Ограничение числа товаров на один заказ"
    )
    is_removed = models.BooleanField(default=False, verbose_name="Удален")

    objects = EbayProductManager()

    def save(self, *args, **kwargs):
        if self.listing.channel.domain.code == "EBAY_MOTORS_US":
            self.EXTRA_IMAGES_LIMIT = 23
        super().save(*args, **kwargs)


class EbayProductSpecification(AbstractEbayAspect):
    product = models.ForeignKey(
        EbayProduct,
        on_delete=models.CASCADE,
        related_name="specifications",
        related_query_name="specification",
    )
