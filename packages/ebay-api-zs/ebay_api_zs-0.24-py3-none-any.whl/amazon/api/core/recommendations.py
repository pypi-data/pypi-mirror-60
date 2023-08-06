from . import utils
from .mws import MWS


class Recommendations(MWS):
    """
    Amazon MWS Recommendations API
    """

    URI = "/Recommendations/2013-04-01"
    VERSION = "2013-04-01"
    NAMESPACE = "{https://mws.amazonservices.com/Recommendations/2013-04-01}"
    NEXT_TOKEN_OPERATIONS = [
        "ListRecommendations",
    ]

    def get_last_updated_time_for_recommendations(self, marketplaceid):
        """
        Checks whether there are active recommendations for each category for the given marketplace, and if there are,
        returns the time when recommendations were last updated for each category.
        """
        data = dict(
            Action="GetLastUpdatedTimeForRecommendations", MarketplaceId=marketplaceid
        )
        return self.make_request(data, "POST")

    @utils.next_token_action("ListRecommendations")
    def list_recommendations(
        self, marketplaceid=None, recommendationcategory=None, next_token=None
    ):
        """
        Returns your active recommendations for a specific category or for all categories for a specific marketplace.
        """
        data = dict(
            Action="ListRecommendations",
            MarketplaceId=marketplaceid,
            RecommendationCategory=recommendationcategory,
        )
        return self.make_request(data, "POST")
