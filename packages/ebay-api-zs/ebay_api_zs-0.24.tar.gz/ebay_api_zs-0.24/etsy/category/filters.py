from django_filters import filterset

from etsy.category.models import EtsyCategory


class EtsyCategoryFilterSet(filterset.FilterSet):
    class Meta:
        model = EtsyCategory
        fields = [
            "category_id",
            "parent_id",
            "level",
            "name",
            "is_leaf",
        ]
