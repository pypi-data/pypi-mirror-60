import datetime

from dateutil.parser import parse

from .base import FulfillmentAPI


class PaymentDisputeAPI(FulfillmentAPI):
    api_location_domain = "apiz"
    resource = "payment_dispute"
    method_type = "GET"
    required_path_params = ["payment_dispute_id"]


class GetPaymentDispute(PaymentDisputeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/fulfillment/resources/payment_dispute/methods/getPaymentDispute
    """


class FetchEvidenceContent(PaymentDisputeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/fulfillment/resources/payment_dispute/methods/fetchEvidenceContent
    """

    required_query_params = ["evidence_id", "file_id"]
    url_postfix = "fetch_evidence_content"


class GetActivities(PaymentDisputeAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/fulfillment/resources/payment_dispute/methods/getActivities
    """

    url_postfix = "activity"


class GetPaymentDisputeSummaries(FulfillmentAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/fulfillment/resources/payment_dispute/methods/getPaymentDisputeSummaries
    """

    api_location_domain = "apiz"
    resource = ""
    method_type = "GET"
    url_postfix = "payment_dispute_summary"
    allowed_query_params = [
        "order_id",
        "buyer_username",
        "open_date_from",
        "open_date_to",
        "payment_dispute_status",
        "limit",
        "offset",
    ]

    def clean_limit(self, limit):
        return super().clean_limit(limit, max_num=200)

    def clean_open_date_to(self, value):
        value = parse(value)
        is_valid = True
        message = ""

        now = datetime.datetime.now()
        if now < value:
            value = now
        elif (now - value).days >= 18 * 30:
            is_valid = False
            message = 'Разница между датой "open_date_to" и настоящим моментом не должна превышать 18 месяцев.'

        return is_valid, message, value

    def clean_open_date_from(self, value):
        value = parse(value)
        message = ""

        now = datetime.datetime.now()
        if now <= value:
            message = (
                'Дата "open_date_from" должна быть более ранней, чем сегодняшняя дата.'
            )
        elif (now - value).days >= 18 * 30:
            message = 'Разница между датой "open_date_from" и настоящим моментом не должна превышать 18 месяцев.'

        is_valid = not bool(message)
        return is_valid, message, value
