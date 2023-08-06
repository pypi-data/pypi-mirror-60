from abc import abstractmethod

from ebay.api.ebay_action import EbayAccountAction, EbayActionError
from ebay.data.marketplace.marketplace_to_site import EbayDomainCodeToSiteID
from ebaysdk.exception import ConnectionError as TradingAPIError
from ebaysdk.trading import Connection as Trading


class EbayTradingAPIActionError(EbayActionError):
    pass


class EbayTradingAPIAction(EbayAccountAction):
    success_message = "Success"
    failure_message = "Failure"
    pagination = False

    @property
    @abstractmethod
    def verb(self):
        pass

    def get_site_id(self, domain_code=None):
        if (not domain_code) and getattr(self, "channel", None):
            domain_code = self.channel.domain.code

        if domain_code:
            try:
                return EbayDomainCodeToSiteID[domain_code]
            except KeyError:
                message = f"Маркетплейс {self.channel.domain.name} не поддерживается Trading API."
                raise EbayTradingAPIActionError(message)

        return EbayDomainCodeToSiteID["default"]

    def get_trading_api(self, site_id, debug=False):
        return Trading(
            siteid=site_id,
            iaf_token=self.account.access_token,
            config_file=None,
            appid=self.credentials.client_id,
            devid=self.credentials.dev_id,
            certid=self.credentials.client_secret,
            debug=debug,
        )

    def get_params(self, **kwargs):
        return {}

    def _clean_data(self, data):
        cleaned_data = {}
        for key, value in data.items():
            if value or isinstance(value, bool):
                if isinstance(value, dict):
                    cleaned_data.update({key: self._clean_data(value)})
                else:
                    cleaned_data.update({key: value})
        return cleaned_data

    def make_request(self, debug=False, clean_data=True, **kwargs):  # noqa: C901
        site_id = self.get_site_id(domain_code=kwargs.get("domain_code", None))

        data = self.get_params(**kwargs)
        if clean_data:
            data = self._clean_data(data)

        try:
            api = self.get_trading_api(debug=debug, site_id=site_id)
            response = api.execute(verb=self.verb, data=data,)
        except TradingAPIError as error:
            response = error.response
            is_success = False
        else:
            is_success = True

        objects = {"response": response}
        results = response.dict()

        if is_success:
            message = self.success_message
            objects.update(
                {"results": results, "data": data,}
            )
        else:
            message = self.failure_message

        if results.get("Errors", None):
            errors = response.dict()["Errors"]
            if not isinstance(errors, list):
                errors = [errors]

            message = "\n".join(
                [
                    error.get("LongMessage", error.get("ShortMessage", ""))
                    for error in errors
                ]
            )
            if not message.strip():
                if is_success:
                    message = self.success_message
                else:
                    message = self.failure_message

            if results["Ack"] == "Failure":
                objects["errors"] = errors
            elif results["Ack"] == "Warning":
                objects["warnings"] = errors

        return is_success, message, objects
