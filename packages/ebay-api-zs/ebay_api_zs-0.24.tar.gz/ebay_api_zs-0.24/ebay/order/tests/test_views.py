from ebay.order.models import EbayOrder
from ebay.order.tests.factories import EbayOrderFactory
from ebay.tests.base import EbayViewSetTest


class EbayOrderViewSetTest(EbayViewSetTest):
    url_path = "ebay:order:order"

    def get_ebay_order(self, order_id):
        url = self.get_url(postfix="detail", id=order_id)
        return self.make_request(method="GET", url_path=url)

    def get_ebay_order_list(self, query_params={}):
        url = self.get_url(postfix="list", query_params=query_params)
        return self.make_request(method="GET", url_path=url)

    def test_get_ebay_order(self):
        order = EbayOrderFactory.create()
        response = self.get_ebay_order(order_id=order.id)
        self.assertStatus(response)
        self.assertEqual(response.json()["id"], str(order.id))

    def test_get_ebay_order_list(self):
        orders = [
            EbayOrderFactory.create(orderId="1"),
            EbayOrderFactory.create(orderId="2"),
            EbayOrderFactory.create(orderId="3"),
        ]

        query = EbayOrder.objects.all()
        self.assertEqual(len(orders), query.count())

        response = self.get_ebay_order_list()
        self.assertStatus(response)
        self.assertEqual(response.json()["count"], query.count())
