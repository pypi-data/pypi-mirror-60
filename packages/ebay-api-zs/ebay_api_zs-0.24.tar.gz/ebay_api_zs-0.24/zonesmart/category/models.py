from django.db import models

from zonesmart.marketplace.models import Domain
from zonesmart.models import UUIDModel


class AbstractMarketplaceCategoryTree(models.Model):
    domain = models.OneToOneField(
        Domain,
        on_delete=models.CASCADE,
        unique=True,
        verbose_name="Домен маркетплейса",
    )

    def __str__(self):
        return f'Дерево категорий для домена "{self.domain}"'

    class Meta:
        abstract = True


class AbstractMarketplaceCategory(UUIDModel):
    category_id = models.CharField(max_length=15, verbose_name="ID категории")
    parent_id = models.CharField(
        max_length=15, verbose_name="ID родительской категории или 0"
    )
    level = models.PositiveSmallIntegerField(
        verbose_name="Уровень вложенности категории"
    )
    name = models.CharField(max_length=100, verbose_name="Название категории")
    name_path = models.CharField(
        blank=True, default="", max_length=500, verbose_name="Путь к категории"
    )
    id_path = models.CharField(
        blank=True, default="", max_length=300, verbose_name="ID пути к категории"
    )
    is_leaf = models.BooleanField(verbose_name="Является листом дерева категорий")

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
