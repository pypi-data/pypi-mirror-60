from django.contrib import admin

from zonesmart.marketplace import models


@admin.register(models.Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = ["name"]
    verbose_name = "Маркетплейс"
    verbose_name_plural = "Маркетплейсы"


@admin.register(models.Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ["name"]
    verbose_name = "Домен"
    verbose_name_plural = "Домены"


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass
