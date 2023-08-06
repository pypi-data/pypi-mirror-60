from django.db import models

from zonesmart.category.models import (
    AbstractMarketplaceCategory,
    AbstractMarketplaceCategoryTree,
)


class EbayCategoryTree(AbstractMarketplaceCategoryTree):
    category_tree_id = models.CharField(
        max_length=10, unique=True, verbose_name="ID дерева категорий"
    )
    category_tree_version = models.CharField(
        max_length=4, blank=True, null=True, verbose_name="Версия дерева категорий"
    )

    class Meta:
        verbose_name = "Дерево категорий для eBay"
        verbose_name_plural = "Деревья категорий для eBay"
        constraints = [
            models.UniqueConstraint(
                fields=["domain", "category_tree_id", "category_tree_version"],
                name="unique_ebay_category_tree",
            )
        ]


class EbayCategory(AbstractMarketplaceCategory):
    category_tree = models.ForeignKey(
        EbayCategoryTree,
        on_delete=models.CASCADE,
        related_name="ebay_product_categories",
        verbose_name="Дерево категорий товаров eBay",
    )
    variationsSupported = models.BooleanField(
        blank=True, default=False, verbose_name="Доступно для групп товаров"
    )
    transportSupported = models.BooleanField(
        blank=True, default=False, verbose_name="Транспортная категория"
    )

    class Meta:
        verbose_name = f"Категория товара eBay"
        verbose_name_plural = f"Категории товара eBay"
        constraints = [
            models.UniqueConstraint(
                fields=["category_id", "category_tree"],
                name="unique_ebay_category_id_for_tree",
            )
        ]
