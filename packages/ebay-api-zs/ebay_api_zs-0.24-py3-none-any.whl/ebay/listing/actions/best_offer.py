# https://developer.ebay.com/DevZone/guides/features-guide/default.html#development/feature-bestoffer.html
from ebay.api.ebay_trading_api_action import EbayTradingAPIAction
from ebay.category.actions import GetEbayCategoryFeatures


class GetEbayCategoryBestOfferInfo(GetEbayCategoryFeatures):
    def get_params(self, category_id, **kwargs):
        kwargs["feature_ids"] = [
            "BestOfferEnabled",
            "BestOfferAutoDeclineEnabled",
            "BestOfferAutoAcceptEnabled",
        ]
        return super().get_params(category_id=category_id, **kwargs)


class GetEbayListingBestOffers(EbayTradingAPIAction):
    # https://developer.ebay.com/DevZone/XML/docs/Reference/eBay/GetBestOffers.html
    description = "Получение предложений покупателей"
    verb = "GetBestOffers"

    def get_params(self, best_offer_id=None, item_id=None, active_only=True, **kwargs):
        if active_only:
            best_offer_status = "Active"
        else:
            best_offer_status = "All"

        return {
            "BestOfferID": best_offer_id,
            "BestOfferStatus": best_offer_status,
            "ItemID": item_id,
        }

    def make_request(self, *args, **kwargs):
        is_success, message, objects = super().make_request(*args, **kwargs)
        if (not is_success) and (
            objects.get("errors", [{}])[0].get("ErrorCode", None) == "20140"
        ):
            is_success = True
            objects["warnings"] = objects.pop("errors")
            objects["results"] = {}
        return is_success, message, objects

    def success_trigger(self, message, objects, **kwargs):
        results = objects["results"]
        if results.get("BestOfferArray", None):
            results = results["BestOfferArray"]["BestOffer"]
        elif results.get("ItemBestOffersArray", None):
            results = results["ItemBestOffersArray"]["ItemBestOffers"][
                "BestOfferArray"
            ]["BestOffer"]
        else:
            results = []

        if not isinstance(results, list):
            results = [results]

        objects["results"] = results
        return super().success_trigger(message, objects, **kwargs)


class RespondToEbayListingBestOffer(EbayTradingAPIAction):
    # https://developer.ebay.com/devzone/xml/docs/reference/ebay/RespondToBestOffer.html
    description = "Получение предложений покупателей"
    verb = "RespondToBestOffer"

    def get_params(
        self,
        action,
        best_offer_id,
        item_id,
        counter_offer_price=None,
        counter_offer_quantity=None,
        seller_response=None,
        **kwargs,
    ):
        if not (action in ["Accept", "Counter", "Decline"]):
            raise AttributeError('Недопустимое значение параметра "action".')

        return {
            "Action": action,
            "BestOfferID": best_offer_id,
            "ItemID": item_id,
            "CounterOfferPrice": counter_offer_price,
            "currencyID": "USD",
            "CounterOfferQuantity": counter_offer_quantity,
            "SellerResponse": seller_response,
        }
