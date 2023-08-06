from etsy.api.etsy_action import EtsyAccountAction

from etsy.order.actions.transaction import FindAllShopTransactions
from etsy.order.models import EtsyReceipt
from etsy.order.serializers.receipt import DownloadEtsyReceiptSerializer
from etsy.order.serializers.transaction import (
    RemoteDownloadReceiptTransactionSerializer,
)


class FindAllShopReceipts(EtsyAccountAction):
    """
    Retrieves a set of Receipt objects associated to a Shop.

    Docs:
    https://www.etsy.com/developers/documentation/reference/receipt#method_findallshopreceipts
    """

    api_method = "findAllShopReceipts"
    params = ["shop_id"]


class RemoteDownloadShopReceiptLIst(FindAllShopReceipts):
    def download_transactions(self, receipt: EtsyReceipt):
        is_success, message, objects = self.raisable_action(
            api_class=FindAllShopTransactions,
            payload={"receipt_id": receipt.receipt_id},
        )
        serializer = RemoteDownloadReceiptTransactionSerializer(
            data=objects["results"], many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(receipt=receipt)

    def success_trigger(self, message: str, objects: dict, **kwargs):
        serializer = DownloadEtsyReceiptSerializer(data=objects["results"], many=True)
        serializer.is_valid(raise_exception=True)
        receipt_list: list = serializer.save(
            marketplace_user_account=self.marketplace_user_account
        )
        for receipt in receipt_list:
            self.download_transactions(receipt)
        return super().success_trigger(message, objects, **kwargs)
