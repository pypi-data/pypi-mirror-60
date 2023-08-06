from django.contrib import admin

import nested_admin
from ebay.policy import models


@admin.register(models.FulfillmentPolicy)
class FulfillmentPolicyAdmin(nested_admin.NestedModelAdmin):

    verbose_name = "Политика фулфилмента"
    verbose_name_plural = "Политики фулфилмента"


@admin.register(models.PaymentPolicy)
class PaymentPolicyAdmin(nested_admin.NestedModelAdmin):

    verbose_name = "Политика оплаты"
    verbose_name_plural = "Политики оплаты"


@admin.register(models.ReturnPolicy)
class ReturnPolicyAdmin(nested_admin.NestedModelAdmin):

    verbose_name = "Политика возврата"
    verbose_name_plural = "Политики возврата"
