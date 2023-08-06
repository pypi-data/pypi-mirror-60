from django.db import models
from model_utils.models import SoftDeletableModel

from etsy.models import EtsyCountry, EtsyRegion

from zonesmart.data.enums import CurrencyCodeEnum
from zonesmart.marketplace.models import MarketplaceEntity, MarketplaceUserAccount
from zonesmart.models import UUIDModel

from zonesmart.models import NestedUpdateOrCreateModelManager


class EtsyShippingTemplateNestedManager(NestedUpdateOrCreateModelManager):
    UPDATE_OR_CREATE_FILTER_FIELDS = {"entries": ["shipping_template_entry_id"]}


class EtsyShippingTemplate(MarketplaceEntity):
    marketplace_user_account = models.ForeignKey(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        limit_choices_to={"marketplace__unique_name": "etsy"},
        related_name="shipping_templates",
        related_query_name="shipping_template",
    )
    # Fields
    shipping_template_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True,
        verbose_name="ID политики доставки",
    )
    title = models.CharField(max_length=100, verbose_name="Название политики",)
    max_processing_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное число дней на обработку заказа",
    )
    min_processing_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное число дней на обработку заказа",
    )
    processing_days_display_label = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Отображаемое число дней на обработку заказа",
    )
    origin_country = models.ForeignKey(
        EtsyCountry,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Страна, из которой отравляется заказ",
    )

    objects = models.Manager()
    nested_objects = EtsyShippingTemplateNestedManager()

    def __str__(self):
        return f"Политика доставки (ID: {self.shipping_template_id})"

    class Meta:
        verbose_name = "Политика доставки Etsy"
        verbose_name_plural = "Политики доставки Etsy"
        constraints = [
            models.UniqueConstraint(
                fields=["marketplace_user_account", "title"],
                name="unique_marketplace_user_account_and_name",
            )
        ]


class EtsyShippingTemplateEntry(UUIDModel, SoftDeletableModel):
    shipping_template = models.ForeignKey(
        EtsyShippingTemplate,
        on_delete=models.CASCADE,
        related_name="entries",
        related_query_name="entry",
        verbose_name="Политика доставки",
    )
    # Fields
    shipping_template_entry_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="ID записи политики доставки",
    )
    currency_code = models.CharField(
        max_length=3,
        blank=True,
        choices=CurrencyCodeEnum,
        default=CurrencyCodeEnum.USD,
        verbose_name="Код валюты",
    )
    destination_country = models.ForeignKey(
        EtsyCountry,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="dest_shipping_templates",
        verbose_name="Страна, в которую отравляется заказ",
    )
    destination_region = models.ForeignKey(
        EtsyRegion,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Регион, в который отравляется заказ",
    )
    primary_cost = models.FloatField(verbose_name="Плата за одиночную доставку",)
    secondary_cost = models.FloatField(verbose_name="Плата за совместную доставку",)
