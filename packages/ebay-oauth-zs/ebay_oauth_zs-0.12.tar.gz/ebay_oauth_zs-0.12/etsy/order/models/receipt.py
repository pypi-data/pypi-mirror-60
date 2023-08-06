from django.db import models

from etsy.data.enums import CurrencyCodeEnum
from etsy.data.enums.receipt_enums import PaymentMethodEnum
from etsy.models import EtsyCountry
from zonesmart.marketplace.models import MarketplaceUserAccount
from zonesmart.order.models import BaseOrder


class EtsyReceipt(models.Model):
    base_order = models.OneToOneField(
        BaseOrder,
        on_delete=models.CASCADE,
        parent_link=True,
        verbose_name="Базовый заказ",
    )
    marketplace_user_account = models.ForeignKey(
        MarketplaceUserAccount,
        on_delete=models.CASCADE,
        related_name="etsy_orders",
        related_query_name="etsy_order",
        verbose_name="Пользовательский аккаунт для маркетплейса",
    )
    receipt_id = models.PositiveIntegerField(primary_key=True, verbose_name="ID",)
    # General
    buyer_user_id = models.PositiveIntegerField(verbose_name="ID покупателя")
    buyer_email = models.EmailField(verbose_name="E-mail покупателя")
    creation_tsz = models.DateTimeField(verbose_name="Дата создания")
    can_refund = models.BooleanField(verbose_name="Возврат возможен")
    last_modified_tsz = models.DateTimeField(verbose_name="Дата обновления")
    # Shipping info
    name = models.CharField(max_length=255, verbose_name="Имя получателя")
    first_line = models.CharField(max_length=255, verbose_name="Первая строка адреса")
    second_line = models.CharField(max_length=255, verbose_name="Вторая строка адреса")
    city = models.CharField(max_length=255, verbose_name="Город")
    state = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Область"
    )
    zip = models.CharField(max_length=255, verbose_name="Почтовый индекс")
    formatted_address = models.CharField(
        max_length=255, verbose_name="Отформатированный адрес доставки"
    )
    country = models.ForeignKey(
        EtsyCountry,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Страна",
    )
    was_shipped = models.BooleanField(verbose_name="Заказ отправлен")
    # Payment
    payment_method = models.CharField(
        max_length=5, choices=PaymentMethodEnum, verbose_name="Тип оплаты"
    )
    payment_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="E-mail покупателя для получения информации о платеже",
    )
    message_from_seller = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Сообщение от продавца"
    )
    message_from_buyer = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Сообщение от покупателя"
    )
    was_paid = models.BooleanField(verbose_name="Заказ оплачен")
    message_from_payment = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Сгенерированное системное сообщение об оплате",
    )
    # Taxes
    total_tax_cost = models.FloatField(verbose_name="Общая сумма налогов")
    total_vat_cost = models.FloatField(verbose_name="Общая сумма НДС")
    # Price
    total_price = models.FloatField(
        verbose_name="Общая сумма заказа",
        help_text="Формируется из цены помноженной на кол-во, не включая налоги и цену доставки",
    )
    total_shipping_cost = models.FloatField(verbose_name="Общая цена доставки")
    currency_code = models.CharField(
        max_length=3, choices=CurrencyCodeEnum, verbose_name="Валюта"
    )
    # Gift
    is_gift = models.BooleanField(verbose_name="Заказ оформлен как подарок")
    needs_gift_wrap = models.BooleanField(verbose_name="Оформлена подарочная упаковка")
    gift_wrap_price = models.FloatField(
        default=0.0, verbose_name="Цена подарочной упаковки"
    )
    gift_message = models.CharField(
        max_length=255, verbose_name="Сообщение получателю подарка"
    )
    # Discounts
    discount_amt = models.FloatField(
        verbose_name="Итоговая сумма скидки",
        help_text="Купоны для бесплатной доставки не учитываются в данной сумме скидки",
    )
    subtotal = models.FloatField(
        verbose_name="Итоговая сумма заказа с учетом скидки",
        help_text="Не включает в себя налоги и цену доставки",
    )
    grandtotal = models.FloatField(
        verbose_name="Итоговая сумма заказа (с учетом скидки, налогов и цены доставки)"
    )
    adjusted_grandtotal = models.FloatField(
        verbose_name="Итоговая сумма заказа после возврата одного или нескольких товаров"
    )
    buyer_adjusted_grandtotal = models.FloatField(
        verbose_name="Итоговая сумма заказа после возврата одного или нескольких товаров с точки зрения покупателя"
    )

    # Not in use (usually not documented by Etsy docs)
    # receipt_type - The enum of the order type this receipt is associated with.
    # order_id - The numeric ID of the order this receipt is associated with.
    # seller_user_id - The numeric ID of the seller for this receipt.
    # seller_email - The email address of the seller.
    # shipped_date - not documented (None)
    # is_overdue - not documented (None)
    # days_from_due_date - not documented (sample data: 18290 (float))
    # shipping_details - not documented, OneToOne object
    # transparent_price_message - not documented (sample data: "Local taxes included (where applicable)" (str))
    # show_channel_badge - not documented (sample data: False (bool))
    # channel_badge_suffix_string - not documented
    # is_dead - not documented (sample data: False (bool))

    class Meta:
        verbose_name = "Заказ Etsy"
        verbose_name_plural = "Заказы Etsy"

    def __str__(self):
        return f"Заказ №{self.receipt_id} от {self.buyer_email}"


class EtsyReceiptShipment(models.Model):
    receipt = models.ForeignKey(
        EtsyReceipt,
        on_delete=models.CASCADE,
        related_name="shipments",
        related_query_name="shipment",
        verbose_name="Заказ Etsy",
    )
    receipt_shipping_id = models.PositiveIntegerField(primary_key=True)
    # Fields
    carrier_name = models.CharField(
        max_length=255, verbose_name="Наименование службы доставки"
    )
    tracking_code = models.CharField(
        max_length=255, verbose_name="Код для отслеживания доставки"
    )
    tracking_url = models.URLField(verbose_name="Сайт службы доставки")
    buyer_note = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Заметка от покупателя"
    )
    notification_date = models.DateTimeField(
        verbose_name="Дата отправки уведомления об отправке заказа"
    )

    class Meta:
        verbose_name = "Информация по доставке заказа"
        verbose_name_plural = "Информация по доставкам заказов"

    def __str__(self):
        return f"Информация по доставке для заказа {self.receipt_shipping_id} ({self.notification_date})"


class EtsyReceiptShippingDetails(models.Model):
    receipt = models.OneToOneField(
        EtsyReceipt,
        on_delete=models.CASCADE,
        related_name="shipping_details",
        verbose_name="Заказ",
    )
    # Fields
    can_mark_as_shipped = models.BooleanField(
        verbose_name="Может быть отмечен как отправленный"
    )
    was_shipped = models.BooleanField(verbose_name="Отправлен")
    is_future_shipment = models.BooleanField(verbose_name="Для ближайшей отправки")
    has_free_shipping_discount = models.BooleanField(
        verbose_name="Использован купон на бесплатную доставку"
    )
    not_shipped_state_display = models.CharField(
        max_length=50, verbose_name="Статус отправки"
    )
    shipping_method = models.CharField(max_length=255, verbose_name="Метод отправки")
    is_estimated_delivery_date_relevant = models.BooleanField(
        verbose_name="Можно указать приблезительную дату доставки"
    )

    class Meta:
        verbose_name = "Информация о доставке"
        verbose_name_plural = "Информации о доставках"

    def __str__(self):
        return f"Информация о доставке для заказа №{self.receipt.id}"
