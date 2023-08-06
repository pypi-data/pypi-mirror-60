from django.db import models

from etsy.listing.models import EtsyListing
from etsy.order.models import EtsyReceipt


class EtsyReceiptTransaction(models.Model):
    receipt = models.ForeignKey(
        EtsyReceipt,
        on_delete=models.CASCADE,
        related_name="transactions",
        related_query_name="transaction",
        verbose_name="Транзакция для заказа",
    )
    # Fields
    transaction_id = models.PositiveIntegerField(primary_key=True, verbose_name="ID")
    seller_user_id = models.PositiveIntegerField(verbose_name="ID продавца")
    buyer_user_id = models.PositiveIntegerField(verbose_name="ID покупателя")
    creation_tsz = models.DateTimeField(verbose_name="Дата и время создания")
    paid_tsz = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата и время оплаты"
    )
    shipped_tsz = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата и время отправки"
    )
    shipping_cost = models.FloatField(verbose_name="Цена доставки")
    listing = models.ForeignKey(
        EtsyListing,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="transactions",
        related_query_name="transaction",
    )
    is_quick_sale = models.BooleanField(verbose_name="Быстрая продажа")
    transaction_type = models.CharField(max_length=30, verbose_name="Тип")
    url = models.URLField(verbose_name="URL")

    # seller_feedback_id - add feedback model
    # buyer_feedback_id - add feedback model

    # Not used fields (usually listing fields)
    # title = models.CharField(max_length=255, verbose_name="Название")
    # description = models.TextField(verbose_name="Описание")
    # price = models.FloatField(verbose_name="Цена")
    # currency_code = models.CharField(max_length=3, choices=CurrencyCodeEnum, verbose_name="Валюта")
    # quantity = models.PositiveIntegerField(verbose_name="Количество")
    # _tags = models.TextField(default="[]", verbose_name="Теги")
    # _materials = models.TextField(default="[]", verbose_name="Материалы")
    # image_listing_id
    # is_digital = models.BooleanField(verbose_name="")
    # file_data

    class Meta:
        verbose_name = "Проданная позиция в заказе"
        verbose_name_plural = "Проданные позиции в заказе"

    def __str__(self):
        return f"{self.Meta.verbose_name} №{self.transaction_id}"
