from .base import AccountAPI


class FulfillmentPolicyAPI(AccountAPI):
    resource = "fulfillment_policy"


class CreateFulfillmentPolicy(FulfillmentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/fulfillment_policy/methods/createFulfillmentPolicy
    """

    method_type = "POST"


class DeleteFulfillmentPolicy(FulfillmentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/fulfillment_policy/methods/deleteFulfillmentPolicy
    """

    method_type = "DELETE"
    required_path_params = ["fulfillment_policy_id"]


class GetFulfillmentPolicy(FulfillmentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/fulfillment_policy/methods/getFulfillmentPolicy
    """

    method_type = "GET"
    required_path_params = ["fulfillment_policy_id"]


class GetFulfillmentPolicies(FulfillmentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/fulfillment_policy/methods/getFulfillmentPolicies
    """

    method_type = "GET"
    required_query_params = ["marketplace_id"]


class GetFulfillmentPolicyByName(FulfillmentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/fulfillment_policy/methods/getFulfillmentPolicyByName
    """

    method_type = "GET"
    url_postfix = "get_by_policy_name"
    required_query_params = ["marketplace_id", "name"]


class UpdateFulfillmentPolicy(FulfillmentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/fulfillment_policy/methods/updateFulfillmentPolicy
    """

    method_type = "PUT"
    required_path_params = ["fulfillment_policy_id"]
