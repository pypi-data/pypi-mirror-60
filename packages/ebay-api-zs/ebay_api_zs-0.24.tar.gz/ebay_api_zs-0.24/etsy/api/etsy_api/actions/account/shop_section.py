from ...base_api import EtsyAPI


class GetEtsyShopSectionList(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_findallshopsections
    """

    api_method_name = "findAllShopSections"
    params = ["shop_id"]


class GetEtsyShopSection(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_getshopsection
    """

    api_method_name = "getShopSection"
    params = ["shop_id", "shop_section_id"]


class CreateEtsyShopSection(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_createshopsection
    """

    api_method_name = "createShopSection"
    params = [
        "shop_id",
        # body
        "title",
    ]


class UpdateEtsyShopSection(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_updateshopsection
    """

    api_method_name = "updateShopSection"
    params = [
        "shop_id",
        "shop_section_id",
        # body
        "title",
    ]


class DeleteEtsyShopSection(EtsyAPI):
    """
    https://www.etsy.com/developers/documentation/reference/shopsection#method_deleteshopsection
    """

    api_method_name = "deleteShopSection"
    params = ["shop_id", "shop_section_id"]
