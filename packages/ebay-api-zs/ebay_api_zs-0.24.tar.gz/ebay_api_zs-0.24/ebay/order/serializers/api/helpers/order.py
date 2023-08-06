from ebay.order.models import EbayOrder


def update_or_create_ebay_order(**kwargs):
    ebay_order, created = EbayOrder.objects.update_or_create(**kwargs)
    return ebay_order, created
