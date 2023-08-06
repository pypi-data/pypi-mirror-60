from model_utils import Choices

ShippingOptionTypeEnum = Choices(
    ("DOMESTIC", "Внутренняя доставка"), ("INTERNATIONAL", "Международная доставка"),
)

CategoryTypeEnum = Choices(
    ("MOTORS_VEHICLES", "Автотранспорт"),
    ("ALL_EXCLUDING_MOTORS_VEHICLES", "Всё, кроме автотранспорта"),
)

ShippingCostTypeEnum = Choices(
    ("CALCULATED", "CALCULATED"),
    ("FLAT_RATE", "LAT_RATE"),
    ("NOT_SPECIFIED", "NOT_SPECIFIED"),
)

RegionTypeEnum = Choices(
    ("COUNTRY", "Страна"),
    ("COUNTRY_REGION", "Страна или регион страны"),
    ("STATE_OR_PROVINCE", "Штат или процинция"),
    ("WORLD_REGION", "Регион мира"),
    ("WORLDWIDE", "Мир"),
)

PaymentInstrumentBrandEnum = Choices(
    ("AMERICAN_EXPRESS", "American Express"),
    ("DISCOVER", "Discover"),
    ("MASTERCARD", "MasterCard"),
    ("VISA", "Visa"),
)

ReturnMethodEnum = Choices(("REPLACEMENT", "Замена"),)

ReturnShippingCostPayerEnum = Choices(("BUYER", "Покупатель"), ("SELLER", "Продавец"),)

RecipientAccountReferenceTypeEnum = Choices(("PAYPAL_EMAIL", "PayPal email"),)

RefundMethodEnum = Choices(
    ("MERCHANDISE_CREDIT", "Продавец предлагает возврат кредитом"),
    ("MONEY_BACK", "Полный возврат продавцом"),
)
