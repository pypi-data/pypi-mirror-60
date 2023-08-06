import factory

from etsy.policy.models.payment_template import EtsyPaymentTemplate
from etsy.tests.factories import EtsyCountryFactory
from zonesmart.marketplace.tests.factories import ChannelFactory


class EtsyPaymentTemplateFactory(factory.DjangoModelFactory):
    channel = factory.SubFactory(ChannelFactory)
    country = factory.SubFactory(EtsyCountryFactory)

    class Meta:
        model = EtsyPaymentTemplate
