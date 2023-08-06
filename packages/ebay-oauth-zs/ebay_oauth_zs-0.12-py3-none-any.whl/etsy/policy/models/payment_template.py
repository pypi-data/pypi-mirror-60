from django.db import models

from etsy.models import EtsyCountry
from zonesmart.marketplace.models import MarketplaceEntity, Channel


class EtsyPaymentTemplate(MarketplaceEntity):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="payment_templates",
        related_query_name="payment_template",
        verbose_name="Магазин",
    )
    # Fields
    payment_template_id = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="ID политики оплаты в системе Etsy"
    )
    # Payment
    allow_bt = models.BooleanField(
        default=False, verbose_name="Принимает банковские переводы"
    )
    allow_check = models.BooleanField(default=False, verbose_name="Принимает чеки")
    allow_mo = models.BooleanField(
        default=False, verbose_name="Принимает платежные поручения"
    )
    allow_other = models.BooleanField(
        default=False, verbose_name="Принимает другие способы оплаты"
    )
    allow_paypal = models.BooleanField(default=False, verbose_name="Принимает PayPal")
    allow_cc = models.BooleanField(
        default=False, verbose_name="Принимает кредитные карты"
    )
    # PayPal
    paypal_email = models.BooleanField(
        blank=True, null=True, verbose_name="PayPal e-mail"
    )
    name = models.BooleanField(blank=True, null=True, verbose_name="Имя продавца")
    # Address
    first_line = models.CharField(
        blank=True, null=True, max_length=255, verbose_name="Первая строка адреса"
    )
    second_line = models.CharField(
        blank=True, null=True, max_length=255, verbose_name="Вторая строка адреса"
    )
    city = models.CharField(blank=True, null=True, max_length=255, verbose_name="Город")
    state = models.CharField(
        blank=True, null=True, max_length=255, verbose_name="Область"
    )
    zip = models.CharField(
        blank=True, null=True, max_length=255, verbose_name="Почтовый индекс"
    )
    country = models.ForeignKey(
        EtsyCountry,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Страна",
    )

    def __str__(self):
        return f"Политика оплаты ({self.payment_template_id})"

    @property
    def shop_id(self):
        return self.channel.shop.shop_id
