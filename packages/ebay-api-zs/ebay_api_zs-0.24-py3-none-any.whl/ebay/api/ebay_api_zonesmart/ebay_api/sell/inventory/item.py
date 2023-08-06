from .base import InventoryAPI


class InventoryItemAPI(InventoryAPI):
    resource = "inventory_item"


# SINGLE ITEM API


class CreateOrReplaceInventoryItem(InventoryItemAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/createOrReplaceInventoryItem
    """

    method_type = "PUT"
    required_path_params = ["sku"]

    def get_success_message(self):
        return f"Товар eBay успешно создан (SKU: {self.path_params['sku']})"

    def get_error_message(self):
        return f"Не удалось создать товар eBay (SKU: {self.path_params['sku']})"


class UpdateInventoryItem(CreateOrReplaceInventoryItem):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/getInventoryItem
    """

    def get_success_message(self):
        return f"Товар eBay успешно обновлён (SKU: {self.path_params['sku']})"

    def get_error_message(self):
        return f"Не удалось обновить товар eBay (SKU: {self.path_params['sku']})"


class GetInventoryItem(InventoryItemAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/getInventoryItem
    """

    method_type = "GET"
    required_path_params = ["sku"]


class GetInventoryItems(InventoryItemAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/getInventoryItems
    """

    method_type = "GET"
    allowed_query_params = ["offset", "limit"]


class DeleteInventoryItem(InventoryItemAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/deleteInventoryItem
    """

    method_type = "DELETE"
    required_path_params = ["sku"]

    def get_success_message(self):
        return f"Товар успешно удалён (SKU: {self.path_params['sku']})"

    def get_error_message(self):
        return f"Не удалось удалить товар (SKU: {self.path_params['sku']})"


# PRODUCT COMPATIBILITY API


class ProductCompatibilityAPI(InventoryItemAPI):
    required_path_params = ["sku"]
    url_postfix = "product_compatibility"


class CreateOrReplaceProductCompatibility(ProductCompatibilityAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/product_compatibility/methods/createOrReplaceProductCompatibility
    """  # noqa

    method_type = "POST"


class GetProductCompatibility(ProductCompatibilityAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/product_compatibility/methods/getProductCompatibility
    """  # noqa

    method_type = "GET"


class DeleteProductCompatibility(ProductCompatibilityAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/product_compatibility/methods/deleteProductCompatibility
    """  # noqa

    method_type = "DELETE"


# BULK API


class BulkInventoryItemAPI(InventoryAPI):
    resource = ""


class BulkUpdatePriceQuantity(BulkInventoryItemAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/bulkUpdatePriceQuantity
    """

    method_type = "POST"
    url_postfix = "bulk_update_price_quantity"


class BulkCreateOrReplaceInventoryItem(BulkInventoryItemAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/bulkCreateOrReplaceInventoryItem
    """  # noqa

    method_type = "POST"
    url_postfix = "bulk_create_or_replace_inventory_item"

    def error_handler(self, response):
        message = ""
        objects = response.json()
        if objects.get("responses", None):
            for error_num, error in enumerate(objects["responses"]):
                errors = error.get("errors", [])
                if errors:
                    message += (
                        f'{error_num+1}) {errors[0]["message"]} (SKU: {error["sku"]})\n'
                    )
            return message, objects
        else:
            return super().error_handler(response=response)


class BulkGetInventoryItem(BulkInventoryItemAPI):
    """
    Docs:
    https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/bulkGetInventoryItem
    """

    method_type = "POST"
    url_postfix = "bulk_get_inventory_item"
