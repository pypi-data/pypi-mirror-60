from factory import SubFactory

from zonesmart.marketplace.tests import factories


class EbayMarketplaceFactory(factories.MarketplaceFactory):
    name = "eBay"
    unique_name = "ebay"


class EbayDomainFactory(factories.DomainFactory):
    name = "US eBay"
    code = "EBAY_US"
    marketplace = SubFactory(EbayMarketplaceFactory)


class EbayMarketplaceUserAccountFactory(factories.MarketplaceUserAccountFactory):
    marketplace = SubFactory(EbayMarketplaceFactory)


class EbayChannelFactory(factories.ChannelFactory):
    name = "American eBay"
    marketplace_user_account = SubFactory(EbayMarketplaceUserAccountFactory)
    domain = SubFactory(EbayDomainFactory)
