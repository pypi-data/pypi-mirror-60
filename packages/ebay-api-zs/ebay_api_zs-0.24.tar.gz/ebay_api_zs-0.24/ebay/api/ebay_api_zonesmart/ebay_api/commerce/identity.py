from .base import CommerceAPI


class IdentityAPI(CommerceAPI):
    api_name = "identity"
    api_version = "v1"


class GetUser(IdentityAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/commerce/identity/resources/user/methods/getUser
    """

    api_location_domain = "apiz"
    resource = "user"
    method_type = "GET"
