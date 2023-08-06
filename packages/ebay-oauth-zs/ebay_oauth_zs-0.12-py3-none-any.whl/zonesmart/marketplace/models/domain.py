from django.db import models

from zonesmart.marketplace.models import Marketplace


class Domain(models.Model):
    marketplace = models.ForeignKey(
        Marketplace,
        on_delete=models.CASCADE,
        related_name="domains",
        related_query_name="domain",
        verbose_name="Маркетплейс",
    )
    name = models.CharField(unique=True, max_length=50, verbose_name="Название домена")
    code = models.CharField(max_length=50, unique=True,)
    description = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="Описание домена"
    )
    url = models.URLField(blank=True, null=True, verbose_name="Адрес")

    class Meta:
        verbose_name = "Домен"
        verbose_name_plural = "Домены"

    def __str__(self):
        return self.name
