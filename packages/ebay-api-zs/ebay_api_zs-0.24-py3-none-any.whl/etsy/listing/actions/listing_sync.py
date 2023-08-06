import json
from datetime import datetime

from etsy.listing.models import EtsyListing
from etsy.api.etsy_action import EtsyEntityAction
from etsy.listing.serializers.listing.remote.upload import (
    RemoteCreateEtsyListingSerializer,
)
from etsy.api.etsy_api.actions.listing import (
    DeleteEtsyListing,
    CreateEtsySingleListing,
    UpdateEtsySingleListing,
    UpdateEtsyListingInventory,
    CreateOrUpdateEtsyListingAttibute,
    DeleteEtsyListingAttibute,
)


class EtsyListingAction(EtsyEntityAction):
    entity_model = EtsyListing
    entity_name = "listing"

    def get_params(self, **kwargs):
        if getattr(self.listing, "listing_id", None):
            kwargs["listing_id"] = self.listing.listing_id
        return super().get_params(**kwargs)

    altering_fields = [
        "listing_id",
        "creation_tsz",
        "ending_tsz",
        "last_modified_tsz",
        "url",
    ]

    def _save_altering_listing_data(self, data: dict):
        for field in self.altering_fields:
            value = data.get(field)
            if field.endswith("tsz"):
                value = datetime.fromtimestamp(value)
            setattr(self.listing, field, value)
        self.listing.save()

    def _delete_altering_listing_data(self):
        for field in self.altering_fields:
            setattr(self.listing, field, None)
        self.listing.save()


class RemoteCreateEtsySingleListing(EtsyListingAction):
    api_class = CreateEtsySingleListing

    def success_trigger(self, message, objects, **kwargs):
        self._save_altering_listing_data(data=objects["results"][0])
        return super().success_trigger(message, objects, **kwargs)


class RemoteUpdateEtsySingleListing(EtsyListingAction):
    api_class = UpdateEtsySingleListing

    def success_trigger(self, message, objects, **kwargs):
        self._save_altering_listing_data(data=objects["results"][0])
        return super().success_trigger(message, objects, **kwargs)


class RemoteDeleteEtsyListing(EtsyListingAction):
    api_class = DeleteEtsyListing
    publish_final_status = False

    def success_trigger(self, message, objects, **kwargs):
        self._delete_altering_listing_data()
        return super().success_trigger(message, objects, **kwargs)


class RemoteCreateOrUpdateEtsyListingAttribute(EtsyListingAction):
    api_class = CreateOrUpdateEtsyListingAttibute


class RemoteDeleteEtsyListingAttribute(EtsyListingAction):
    api_class = DeleteEtsyListingAttibute


class RemoteCreateOrUpdateEtsyListingProducts(EtsyListingAction):
    api_class = UpdateEtsyListingInventory

    def get_params(self, **kwargs):
        # temporary adding properies manually
        kwargs["products"][0]["property_values"] = [
            {"property_id": 200, "values": [1213]},
            {"property_id": 52047899002, "values": [1213]},
        ]
        kwargs["products"][1]["property_values"] = [
            {"property_id": 200, "values": [1]},
            {"property_id": 52047899002, "values": [1213]},
        ]
        _on_property = ",".join(
            [
                str(property_value["property_id"])
                for property_value in kwargs["products"][0]["property_values"]
            ]
        )
        kwargs.update(
            {
                "price_on_property": _on_property,
                "quantity_on_property": _on_property,
                "sku_on_property": _on_property,
            }
        )
        kwargs["products"] = json.dumps(kwargs.get("products", []))
        params = super().get_params(**kwargs)
        print(params)
        return params


class SyncEtsyListing(EtsyListingAction):
    publish_final_status = True

    def create_single_listing(self, data: dict):
        return self.raisable_action(RemoteCreateEtsySingleListing, **data,)

    def update_single_listing(self, data: dict):
        return self.raisable_action(RemoteUpdateEtsySingleListing, **data,)

    def create_or_update_listing_attribute(self, data: dict):
        return self.raisable_action(RemoteCreateOrUpdateEtsyListingAttribute, **data,)

    def delete_listing_attribute(self, property_id: int):
        return self.raisable_action(
            RemoteDeleteEtsyListingAttribute, property_id=property_id,
        )

    def create_or_update_products(self, data: dict):
        return self.raisable_action(RemoteCreateOrUpdateEtsyListingProducts, **data,)

    def make_request(self, **kwargs):
        data = RemoteCreateEtsyListingSerializer(self.listing).data
        try:
            # create or update single listing
            if self.listing.published:
                # create single listing
                print("Обновление листинга Etsy.")
                self.update_single_listing(data)
            else:
                # update single listing
                print("Создание листинга Etsy.")
                self.create_single_listing(data)
            # create or update listing products
            self.create_or_update_products(data)
            # create or update listing attributes
            for attribute_data in data.get("attributes", []):
                self.create_or_update_listing_attribute(attribute_data)
        except self.exception_class as error:
            is_success = False
            message = f"Не удалось синхронизировать листинг с Etsy.\n{error}"
            objects = {"response": getattr(error, "response", None)}
        else:
            is_success = True
            message = f"Листинг успешно синхронизирован с Etsy."
            objects = {}

        return is_success, message, objects
