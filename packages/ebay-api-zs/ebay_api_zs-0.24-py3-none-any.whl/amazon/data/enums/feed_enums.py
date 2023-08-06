FeedProcessingStatusEnum = (
    (
        "_AWAINTING_ASYNCHRONOUS_REPLY_",
        "Запрос в обработке, но ожидает информации извне",
    ),
    ("_CANCELLED_", "Запрос отменен из-за возникшей ошибки"),
    ("_DONE_", "Обработка завершена"),
    ("_IN_PROGRESS_", "Запрос обрабатывается"),
    ("_IN_SAFETY_NET_", "Запрос в обработке, но может содержать ошибку"),
    ("_SUBMITTED_", "Запрос принят, но обработка не начата"),
    ("_UNCONFIRMED_", "Запрос ожидает принятия"),
)

FeedTypeEnum = (
    # product
    ("_POST_FLAT_FILE_INVLOADER_DATA_", "Inventory Loader Feed"),
    ("_POST_FLAT_FILE_LISTINGS_DATA_", "Listings Feed"),
    ("_POST_FLAT_FILE_BOOKLOADER_DATA_", "Book Loader Feed"),
    ("_POST_FLAT_FILE_CONVERGENCE_LISTINGS_DATA_", "Music Loader Feed"),
    ("_POST_FLAT_FILE_LISTINGS_DATA_", "Video Loader Feed"),
    (
        "_POST_FLAT_FILE_PRICEANDQUANTITYONLY_UPDATE_DATA_",
        "Price and Quantity Update Feed",
    ),
    ("_POST_UIEE_BOOKLOADER_DATA_", "UIEE Inventory Feed"),
    # order
    ("_POST_FLAT_FILE_ORDER_ACKNOWLEDGEMENT_DATA_", "Order Acknowledgement Feed"),
    ("_POST_FLAT_FILE_PAYMENT_ADJUSTMENT_DATA_", "Order Adjustments Feed"),
    ("_POST_FLAT_FILE_FULFILLMENT_DATA_", "Order Fulfillment Feed"),
    # FBA
    ("_POST_FLAT_FILE_FULFILLMENT_ORDER_REQUEST_DATA_", "FBA Fulfillment Order Feed"),
    (
        "_POST_FLAT_FILE_FULFILLMENT_ORDER_CANCELLATION_REQUEST_DATA_",
        "FBA Fulfillment Order Cancellation Feed",
    ),
    ("_POST_FLAT_FILE_FBA_CREATE_INBOUND_PLAN_", "Create Inbound Shipment Plan Feed"),
    (
        "_POST_FLAT_FILE_FBA_UPDATE_INBOUND_PLAN_",
        "FBA Update Inbound Shipment Plan Feed",
    ),
    ("_POST_FLAT_FILE_FBA_CREATE_REMOVAL_", "FBA Create Removal Feed"),
)
