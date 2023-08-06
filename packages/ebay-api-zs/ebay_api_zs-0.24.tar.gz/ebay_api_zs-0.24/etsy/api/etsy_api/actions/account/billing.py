from ...base_api import EtsyAPI


class GetUserChargesMetadata(EtsyAPI):
    """
    Metadata for the set of BillCharges objects associated to a User

    Docs:
    https://www.etsy.com/developers/documentation/reference/billcharge#section_getuserchargesmetadata
    """

    api_method_name = "getUserChargesMetadata"
    params = ["user_id"]


class FindAllUserCharges(EtsyAPI):
    """
    Retrieves a set of BillCharge objects associated to a User.
    NOTE: from 8/8/12 the min_created and max_created arguments will be mandatory
    and can be no more than 31 days apart.

    Dev notes:
    - min_created is required.
        1) Usage pattern:
        ###############################################
        ### from datetime import datetime           ###
        ###                                         ###
        ### now = datetime.now()                    ###
        ### delta = datetime.timedelta(days=31)     ###
        ### min_created = (now - delta).timestamp() ###
        ###############################################
        2) Another way is call GetUserChargesMetadata and get min_create_date from
        the results.
    - transaction type bills missing (not returned with response)

    Docs:
    https://www.etsy.com/developers/documentation/reference/billcharge#method_findallusercharges
    """

    api_method_name = "findAllUserCharges"
    params = [
        "user_id",
        # body
        "min_created",
        "max_created",
        "limit",
        "offset",
        "page",
        "sort_order",
    ]


class GetUserBillingOverview(EtsyAPI):
    """
    Retrieves the user's current balance.

    Docs:
    https://www.etsy.com/developers/documentation/reference/billingoverview#method_getuserbillingoverview
    """

    api_method_name = "getUserBillingOverview"
    params = ["user_id"]
