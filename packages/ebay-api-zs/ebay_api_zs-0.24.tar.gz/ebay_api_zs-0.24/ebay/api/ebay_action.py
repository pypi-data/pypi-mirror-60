from ebay.api.ebay_access import EbayAPIAccess, EbayAPIAccessError

from zonesmart.marketplace.api.marketplace_action import (
    MarketplaceAccountAction,
    MarketplaceAction,
    MarketplaceChannelAction,
    MarketplaceEntityAction,
)
from zonesmart.utils.logger import get_logger

logger = get_logger(app_name=__file__)


class EbayActionError(EbayAPIAccessError):
    response = None


class EbayAction(EbayAPIAccess, MarketplaceAction):
    description = "Действие eBay"
    api_class = None
    exception_class = EbayActionError
    next_token_action = False

    def _refresh_access_token(self, only_if_expired=True):
        updated = False
        if (not only_if_expired) or self.account.access_token_expired():
            token_data = self.get_refreshed_token_data(
                refresh_token=self.account.refresh_token
            )
            self.account.save_token_data(token_data)
            logger.info("Токен доступа успешно обновлён")
            updated = True
        return updated

    def before_request(self, *args, **kwargs):
        self._refresh_access_token()

    def get_path_params(self, **kwargs):
        return {
            param: kwargs.get(param, None)
            for param in self.api_class.required_path_params
        }

    def get_query_params(self, **kwargs):
        return {
            param: kwargs.get(param, None)
            for param in [
                *self.api_class.required_query_params,
                *self.api_class.allowed_query_params,
            ]
        }

    def make_request(self, **kwargs):
        if not getattr(self, "api_class", None):
            raise AttributeError("Необходимо задать атрибут api_class.")

        api = self.api_class(
            access_token=self.account.access_token,
            sandbox=self.is_sandbox,
            marketplace_id=self.marketplace_id,
        )

        if getattr(self, "payload_serializer", None):
            self.payload = self.get_payload(
                serializer=self.payload_serializer, instance=self.entity,
            )
        else:
            self.payload = kwargs.get("payload", None)

        self.path_params = self.get_path_params(**kwargs)
        self.query_params = self.get_query_params(**kwargs)

        api_kwargs = {
            "payload": self.payload,
            "path_params": self.path_params,
            "query_params": self.query_params,
        }

        if not self.next_token_action:
            return api.make_request(**api_kwargs)
        else:
            next_url = None
            results = []

            while True:
                is_success, message, objects = api.make_request(
                    next_url=next_url, **api_kwargs,
                )
                if not is_success:
                    return is_success, message, objects

                results += [objects["results"]]
                next_url = objects.get("next", None)
                if not next_url:
                    break

            objects["results"] = results
            return True, "", objects


class EbayAccountAction(EbayAction, MarketplaceAccountAction):
    pass


class EbayChannelAction(EbayAction, MarketplaceChannelAction):
    pass


class EbayEntityAction(EbayAction, MarketplaceEntityAction):
    pass
