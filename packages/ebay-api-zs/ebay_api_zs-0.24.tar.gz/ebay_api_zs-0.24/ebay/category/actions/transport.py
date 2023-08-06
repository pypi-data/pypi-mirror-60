from ebay.api.ebay_action import EbayAction
from ebay.category.models import EbayCategory, EbayCategoryTree
from ebay_api.sell.metadata.marketplace import GetAutomotivePartsCompatibilityPolicies


class GetCompatibilitySupportedCategories(EbayAction):
    description = "Получение транспортных категорий"
    api_class = GetAutomotivePartsCompatibilityPolicies

    def success_trigger(self, message, objects, **kwargs):
        if kwargs.get("only_supported", False):
            objects["results"] = [
                item
                for item in objects["results"]["automotivePartsCompatibilityPolicies"]
                if len(item) > 2
            ]
        return super().success_trigger(message, objects, **kwargs)


class MarkCompatibilitySupportedEbayDomainCategories(
    GetCompatibilitySupportedCategories
):
    description = "Обновление поля transportSupported категорий домена eBay."

    def success_trigger(
        self, message: str, objects: dict, marketplace_id: str, **kwargs
    ):
        is_success, message, comp_supported_categories = super().success_trigger(
            message, objects, only_supported=True
        )

        comp_supported_category_ids = [
            category_data["categoryId"]
            for category_data in comp_supported_categories["results"]
        ]
        # filter categories by domain
        categories = EbayCategory.objects.filter(
            category_tree__domain__code=marketplace_id,
        )
        # set all categories as not supporting transport
        categories.update(transportSupported=False)
        # update transport supporting categories
        categories.filter(category_id__in=comp_supported_category_ids).update(
            transportSupported=True
        )

        message = (
            f"Данные о транспортных категориях домена {marketplace_id} "
            f"успешно загружены ({len(comp_supported_category_ids)} категорий)."
        )

        return is_success, message, objects


class MarkCompatibilitySupportedCategories:
    description = "Получение и сохранение транспортных категорий всех доменов eBay."

    def __call__(self):
        action = MarkCompatibilitySupportedEbayDomainCategories()
        for category_tree in EbayCategoryTree.objects.all():
            is_success, message, obj = action(marketplace_id=category_tree.domain.code)
