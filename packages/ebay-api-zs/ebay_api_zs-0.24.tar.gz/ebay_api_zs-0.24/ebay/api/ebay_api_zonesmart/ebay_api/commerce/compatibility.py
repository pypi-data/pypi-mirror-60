from .taxonomy import CategoryTreeAPI


class GetCompatibilityProperties(CategoryTreeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getCompatibilityProperties
    """

    url_postfix = "get_compatibility_properties"
    required_query_params = ["category_id"]


class GetCompatibilityPropertyValues(CategoryTreeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/taxonomy/resources/category_tree/methods/getCompatibilityPropertyValues
    """

    url_postfix = "get_compatibility_property_values"
    required_query_params = ["compatibility_property", "category_id"]
    allowed_query_params = ["filter"]
