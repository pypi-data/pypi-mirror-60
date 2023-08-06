from amazon.account.tests.factories import AmazonUserAccountFactory
from amazon.tests.factories import AmazonChannelFactory

from zonesmart.tests.base import BaseActionTest


class AmazonActionTest(BaseActionTest):
    def setUp(self):
        super().setUp()
        self.channel = AmazonChannelFactory.create()
        self.domain = self.channel.domain
        self.marketplace_user_account = self.channel.marketplace_user_account
        self.user_account = AmazonUserAccountFactory.create(
            marketplace_user_account=self.marketplace_user_account,
        )

    def perform_action(self, *args, **kwargs):
        kwargs["retry_if_500"] = False
        return super().perform_action(*args, **kwargs)
