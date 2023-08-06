from django.contrib import admin

import nested_admin
from ebay.negotiation import models


@admin.register(models.EbayEligibleItem)
class EbayEligibleItemAdmin(admin.ModelAdmin):
    pass


class EbayBuyerOfferPriceInline(nested_admin.NestedTabularInline):
    model = models.EbayBuyerOfferPrice
    max_num = 1
    can_delete = False


class EbayBuyerOfferedItemInline(nested_admin.NestedStackedInline):
    model = models.EbayBuyerOfferedItem
    extra = 0
    inlines = [EbayBuyerOfferPriceInline]


class EbayBuyerOfferDurationInline(nested_admin.NestedTabularInline):
    model = models.EbayBuyerOfferDuration
    max_num = 1
    can_delete = False


@admin.register(models.EbayBuyerOffer)
class EbayBuyerOfferAdmin(nested_admin.NestedModelAdmin):
    inlines = [
        EbayBuyerOfferedItemInline,
        EbayBuyerOfferDurationInline,
    ]


@admin.register(models.EbayMessage)
class EbayMessageAdmin(admin.ModelAdmin):
    pass
