from django.utils import timezone

from ebay.order.models import EbayOrder
from factory import DjangoModelFactory, SubFactory

from zonesmart.marketplace.tests.factories import MarketplaceUserAccountFactory


class EbayOrderFactory(DjangoModelFactory):
    class Meta:
        model = EbayOrder
        django_get_or_create = ["marketplace_user_account"]

    marketplace_user_account = SubFactory(MarketplaceUserAccountFactory)
    buyer_username = "TestBuyer"
    creationDate = timezone.now()
    lastModifiedDate = timezone.now()
    legacyOrderId = "1"
    orderFulfillmentStatus = "IN_PROGRESS"
    orderId = "1"
    orderPaymentStatus = "PAID"
    sellerId = "1"
