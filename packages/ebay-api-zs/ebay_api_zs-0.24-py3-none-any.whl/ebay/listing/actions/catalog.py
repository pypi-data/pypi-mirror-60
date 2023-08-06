from ebay.api.ebay_action import EbayAccountAction
from ebay_api.commerce.catalog import GetProduct


class RemoteGetEbayCatalogProductByEPID(EbayAccountAction):
    api_class = GetProduct
