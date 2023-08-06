from dateutil.parser import parse
from ebay.api.ebay_action import EbayAccountAction
from ebay_api.sell.fulfillment import payment_dispute as dispute_api


class GetEbayAccountPaymentDispute(EbayAccountAction):
    description = "Получение информации о споре с пользователем"
    api_class = dispute_api.GetPaymentDispute


class GetEbayAccountPaymentDisputeList(EbayAccountAction):
    description = "Получение информации о спорах с пользователями"
    api_class = dispute_api.GetPaymentDisputeSummaries

    def get_query_params(self, **kwargs):
        open_date_from = kwargs.get("open_date_from", None)
        open_date_to = kwargs.get("open_date_to", None)
        if open_date_from and open_date_to:
            date_to = parse(open_date_to)
            date_from = parse(open_date_from)
            if (date_to - date_from).days >= 90:
                raise AttributeError(
                    'Разница между датами "open_date_to" и "open_date_from" не должна превышать 3 месяца.'
                )
            elif date_to <= date_from:
                raise AttributeError(
                    'Дата "open_date_from" должна быть более ранней, чем "open_date_to".'
                )
        return super().get_query_params(**kwargs)
