from ebay.negotiation.models import EbayMessage
from ebay.negotiation.tests.factories import EbayMessageFactory
from ebay.tests.base import EbayViewSetTest
from rest_framework import status


class EbayNegotiationViewSetTest(EbayViewSetTest):
    url_path = "ebay:negotiation:message"

    def get_ebay_message(self, message_id):
        url = self.get_url(postfix="detail", message_id=message_id)
        return self.make_request(method="GET", url_path=url)

    def get_ebay_message_list(self, query_params={}):
        url = self.get_url(postfix="list", query_params=query_params)
        return self.make_request(method="GET", url_path=url)

    def download_ebay_message_list(self):
        url = self.get_url(
            postfix="remote-download-list",
            marketplace_user_account_id=self.marketplace_user_account.id,
        )
        return self.make_request(method="GET", url_path=url)

    def test_get_ebay_message(self):
        message = EbayMessageFactory.create()
        response = self.get_ebay_message(message_id=message.message_id)
        self.assertStatus(response)
        self.assertEqual(response.json()["message_id"], str(message.message_id))

    def test_get_ebay_message_list(self):
        messages = [
            EbayMessageFactory.create(message_id="1"),
            EbayMessageFactory.create(message_id="2"),
            EbayMessageFactory.create(message_id="3"),
        ]

        query = EbayMessage.objects.all()
        self.assertEqual(len(messages), query.count())

        response = self.get_ebay_message_list()
        self.assertStatus(response)
        self.assertEqual(response.json()["count"], query.count())

    def test_download_message_list(self):
        response = self.download_ebay_message_list()
        self.assertStatus(response, status=status.HTTP_201_CREATED)
