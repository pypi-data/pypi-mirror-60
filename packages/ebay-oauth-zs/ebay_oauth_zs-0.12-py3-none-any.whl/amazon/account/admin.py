from django.contrib import admin

from amazon.account import models


@admin.register(models.AmazonUserAccount)
class AmazonAccountAdmin(admin.ModelAdmin):
    exclude = []
