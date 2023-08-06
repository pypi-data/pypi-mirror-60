from django.db import models

from zonesmart.category.models import (
    AbstractMarketplaceCategory,
    AbstractMarketplaceCategoryTree,
)


class EtsyCategoryTree(AbstractMarketplaceCategoryTree):
    category_tree_version = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Версия дерева категорий"
    )

    class Meta:
        verbose_name = "Дерево категорий для Etsy"
        verbose_name_plural = "Деревья категорий для Etsy"


class EtsyCategory(AbstractMarketplaceCategory):
    category_tree = models.ForeignKey(
        EtsyCategoryTree,
        on_delete=models.CASCADE,
        related_name="etsy_product_categories",
        verbose_name="Дерево категорий товаров Etsy",
    )
    old_category_id = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="ID старой версии категории"
    )

    class Meta:
        verbose_name = f"Категория товара Etsy"
        verbose_name_plural = f"Категории товара Etsy"
        constraints = [
            models.UniqueConstraint(
                fields=["category_id", "category_tree"],
                name="unique_etsy_category_id_for_tree",
            )
        ]
