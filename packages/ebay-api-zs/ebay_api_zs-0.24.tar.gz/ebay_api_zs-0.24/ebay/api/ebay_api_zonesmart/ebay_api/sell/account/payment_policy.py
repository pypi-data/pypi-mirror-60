from .base import AccountAPI


class PaymentPolicyAPI(AccountAPI):
    resource = "payment_policy"


class CreatePaymentPolicy(PaymentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/payment_policy/methods/createPaymentPolicy
    """

    method_type = "POST"


class DeletePaymentPolicy(PaymentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/payment_policy/methods/deletePaymentPolicy
    """

    method_type = "DELETE"
    required_path_params = ["payment_policy_id"]


class GetPaymentPolicy(PaymentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/payment_policy/methods/getPaymentPolicy
    """

    method_type = "GET"
    required_path_params = ["payment_policy_id"]


class GetPaymentPolicies(PaymentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/payment_policy/methods/getPaymentPolicies
    """

    method_type = "GET"
    required_query_params = ["marketplace_id"]


class GetPaymentPolicyByName(PaymentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/payment_policy/methods/getPaymentPolicyByName
    """

    method_type = "GET"
    url_postfix = "get_by_policy_name"
    required_query_params = ["marketplace_id", "name"]


class UpdatePaymentPolicy(PaymentPolicyAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/account/resources/payment_policy/methods/updatePaymentPolicy
    """

    method_type = "PUT"
    required_path_params = ["payment_policy_id"]
