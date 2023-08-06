from ebay.negotiation.models import EbayEligibleItem


def deactivate_eligible_items(id_list: list = None):
    if id_list is None:
        id_list = list()

    queryset = EbayEligibleItem.objects.all()
    if id_list:
        queryset = queryset.filter(id__in=id_list)

    queryset.update(active=False)
