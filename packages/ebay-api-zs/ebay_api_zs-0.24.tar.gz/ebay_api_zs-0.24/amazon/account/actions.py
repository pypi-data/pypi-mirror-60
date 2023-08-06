from amazon.api.amazon_action import AmazonSellerAction
from amazon.data.enums import MarketplaceToHost
from amazon.utils import jsonify_object_dict


class GetAmazonMarketplaceParticipations(AmazonSellerAction):
    def make_request(self):
        is_success, message, objects = self.api.list_marketplace_participations()
        if is_success:
            message = f"Список доступных для пользователя маркетплейсов Amazon успешно получен.\n{message}"
            objects["results"] = jsonify_object_dict(
                [
                    marketplace
                    for marketplace in list(
                        objects["response"].parsed["ListMarketplaces"]["Marketplace"]
                    )
                    if marketplace["MarketplaceId"]["value"] in MarketplaceToHost
                ]
            )
        else:
            message = f"Не удалось получить список доступных для пользователя маркетплейсов Amazon.\n{message}"
        return is_success, message, objects
