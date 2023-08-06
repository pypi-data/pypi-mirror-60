from typing import Tuple

from ebay.order.models import CancelRequest, CancelStatus, EbayOrder


def update_or_create_cancel_status(
    ebay_order: EbayOrder, data: dict
) -> Tuple[CancelStatus, bool]:
    # Pop cancel request data list
    cancel_request_data_list = data.pop("cancel_requests")
    # Create or update CancelStatus
    instance: CancelStatus
    created: bool
    instance, created = CancelStatus.objects.update_or_create(
        order=ebay_order, defaults=data
    )
    # For each cancel request data create or update CancelRequest
    for cancel_request_data in cancel_request_data_list:
        cancel_request, created = create_or_update_cancel_request(
            cancel_status=instance, data=cancel_request_data
        )
    return instance, created


def create_or_update_cancel_request(
    cancel_status: CancelStatus, data: dict
) -> Tuple[CancelRequest, bool]:
    instance: CancelRequest
    created: bool
    instance, created = CancelRequest.objects.update_or_create(
        cancel_status=cancel_status, defaults=data
    )
    return instance, created
