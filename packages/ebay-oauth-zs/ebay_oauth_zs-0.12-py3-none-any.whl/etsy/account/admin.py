from django.contrib import admin

import nested_admin
from etsy.account.models import EtsyUserAccount, EtsyShop, EtsyShopSection


@admin.register(EtsyUserAccount)
class EtsyUserAccountAdminModel(admin.ModelAdmin):
    pass


class EtsyShopSectionInline(nested_admin.NestedTabularInline):
    model = EtsyShopSection
    can_delete = False
    extra = 0
    editable = False


@admin.register(EtsyShop)
class EtsyShopAdmin(nested_admin.NestedModelAdmin):
    inlines = [EtsyShopSectionInline]
