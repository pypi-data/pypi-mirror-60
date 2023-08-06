from typing import Optional, Type

from ebay.api.ebay_action import EbayAccountAction, EbayChannelAction
from ebay.category import helpers
from ebay.category.models import EbayCategory
from ebay.listing.actions.old_style_listing import GetEbayOldStyleListing
from ebay.listing.actions.old_style_listing_migration import MigrateEbayOldStyleListings
from ebay.listing.serializers.listing.remote_api.listing import (
    DownloadEbayListingSerializer,
)
from ebay.location.actions import RemoteDownloadEbayLocation
from ebay.location.models import EbayLocation
from ebay.policy.actions import (
    GetPolicyAction,
    RemoteDownloadFulfillmentPolicy,
    RemoteDownloadPaymentPolicy,
    RemoteDownloadReturnPolicy,
)
from ebay.policy.models import (
    AbstractPolicy,
    FulfillmentPolicy,
    PaymentPolicy,
    ReturnPolicy,
)
from ebay_api.sell.inventory import item, item_group, offer

from zonesmart.product.models import BaseProduct, ProductImage


class RemoteGetEbayItem(EbayAccountAction):
    api_class = item.GetInventoryItem


class RemoteGetEbayOffer(EbayAccountAction):
    api_class = offer.GetOffer


class RemoteGetEbayProductGroup(EbayAccountAction):
    api_class = item_group.GetInventoryItemGroup


class RemoteGetEbayOfferByItemSKU(EbayAccountAction):
    api_class = offer.GetOffers

    def success_trigger(self, message, objects, **kwargs):
        offers_num = objects["results"].get("total", 0)
        if offers_num == 0:
            objects["results"] = []
        elif offers_num == 1:
            objects["results"] = objects["results"]["offers"][0]
        else:
            raise self.exception_class("Item has more than 1 offer.")

        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadEbayListing(EbayAccountAction):
    description = "Загрузка товара с eBay"

    def remote_get_item(self, sku: str):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEbayItem, sku=sku
        )
        return objects["results"]

    def remote_get_offer(self, offerId: str):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEbayOffer, offerId=offerId
        )
        return objects["results"]

    def remote_get_offer_by_sku(self, sku: str):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEbayOfferByItemSKU, sku=sku
        )
        return objects["results"]

    def remote_get_product_group(self, listing_sku: str):
        is_success, message, objects = self.raisable_action(
            api_class=RemoteGetEbayProductGroup, inventoryItemGroupKey=listing_sku,
        )
        return objects["results"]

    def remote_get_old_style_listing(self, listingId: str):
        is_success, message, objects = self.raisable_action(
            api_class=GetEbayOldStyleListing, listingId=listingId,
        )
        return objects["results"]

    def make_request(self, listingId: str, **kwargs):
        listing_data = self.remote_get_old_style_listing(listingId=listingId)
        if listing_data.get("Variations", None):
            # listing with variations case
            groupListingId = listingId
            listing_sku = listing_data["SKU"]
            # download products group data
            product_group_data = self.remote_get_product_group(listing_sku=listing_sku)
            # download products data
            product_data_list = []
            for product_sku in product_group_data["variantSKUs"]:
                item_data = self.remote_get_item(sku=product_sku)
                offer_data = self.remote_get_offer_by_sku(sku=product_sku)
                product_data_list.append({**item_data, **offer_data})
            # pack data
            objects = {
                "has_variations": True,
                "groupListingId": groupListingId,
                "listing_sku": listing_sku,
                "group": product_group_data,
                "products": product_data_list,
            }
        else:
            # single listing case
            # download product data
            item_data = self.remote_get_item(sku=listing_data["SKU"])
            offer_data = self.remote_get_offer_by_sku(sku=listing_data["SKU"])
            product_data = {**item_data, **offer_data}
            # pack data
            objects = {
                "has_variations": False,
                "products": [product_data],
            }

        return True, "Товары, предложения и группы успешно загружены.", objects

    def get_policy(
        self,
        policy_id: str,
        model: Type[AbstractPolicy],
        action: Type[GetPolicyAction],
        action_key: str,
    ) -> Type[AbstractPolicy]:
        policy = None
        # Try to get policy or download by policy action
        try:
            policy = model.objects.get(channel=self.channel, policy_id=policy_id)
        except model.DoesNotExist:
            download_action = action(channel=self.channel)
            kwargs = {action_key: policy_id}
            is_success, message, objects = download_action(**kwargs)
            if is_success:
                policy = model.objects.get(channel=self.channel, policy_id=policy_id)
        # Return policy
        return policy

    def get_location(self, merchant_location_key: str) -> Optional[EbayLocation]:
        location = None

        try:
            location = EbayLocation.objects.get(
                marketplace_user_account=self.marketplace_user_account,
                merchantLocationKey=merchant_location_key,
            )
        except EbayLocation.DoesNotExist:
            download_action = RemoteDownloadEbayLocation(
                marketplace_user_account=self.marketplace_user_account
            )
            is_success, message, objects = download_action(
                merchantLocationKey=merchant_location_key
            )
            if is_success:
                location = EbayLocation.objects.get(
                    marketplace_user_account=self.marketplace_user_account,
                    merchantLocationKey=merchant_location_key,
                )

        return location

    def success_trigger(self, message: str, objects: dict, **kwargs):
        has_variations = objects["has_variations"]

        print(objects)

        product = objects["products"][0]
        if not has_variations:
            listing_description = product["listingDescription"]
            image_urls = product["product"]["imageUrls"]
            listing_sku = product["product"]["sku"]
            title = product["product"]["title"]
            aspects = product["product"]["aspects"]
        else:
            listing_description = objects["group"]["description"]
            image_urls = objects["group"]["imageUrls"]
            listing_sku = objects["listing_sku"]
            title = objects["group"]["title"]
            for product in objects["products"]:
                product["description"] = listing_description
                product.update(product.pop("pricingSummary")["price"])
                product.update(product.pop("product"))
            aspects = objects["group"]["variesBy"]["specifications"]

        merchant_location_key = product["merchantLocationKey"]
        policies = product["listingPolicies"]
        payment_policy_id = policies["paymentPolicyId"]
        return_policy_id = policies["returnPolicyId"]
        fulfillment_policy_id = policies["fulfillmentPolicyId"]
        sku = product["sku"]

        # Create product images or get from db if exists already
        existed_product_images = ProductImage.objects.filter(image_url__in=image_urls)
        product_images = ProductImage.objects.bulk_create(
            [
                ProductImage(image_url=url)
                for url in image_urls
                if not existed_product_images.filter(image_url=url).exists()
            ]
        )
        for existed_product_image in existed_product_images:
            product_images.append(existed_product_image)
        main_image, extra_images = product_images[0], product_images[1:]

        # Ebay category get
        ebay_category = EbayCategory.objects.get(
            category_tree__domain=self.channel.domain,
            category_id=product["categoryId"],
        )

        # Aspects
        # Get aspects for category
        # Separate listing and product aspects
        is_success, message, aspect_data_list = helpers.get_category_aspects(
            category=ebay_category,
            marketplace_user_account=self.marketplace_user_account,
        )

        listing_aspects = list()
        product_aspects = list()

        for aspect_data in aspect_data_list:
            aspect_name = aspect_data["localizedAspectName"]
            if aspect_name in aspects:
                d = {"name": aspect_name, "value": aspects.pop(aspect_name)[0]}
                if aspect_data["aspectConstraint"]["aspectEnabledForVariations"]:
                    listing_aspects.append(d)
                else:
                    product_aspects.append(d)

        # Add listing aspects
        objects["aspects"] = listing_aspects

        # Add main, extra images & aspects for each product
        # TODO: imrove perfomance
        for p in objects["products"]:
            p["main_image"] = main_image.id
            p["extra_images"] = [extra_image.id for extra_image in extra_images]
            p["specifications"] = product_aspects

        # Serialize downloaded data for listing object
        objects["listing_description"] = listing_description
        objects["listing_sku"] = listing_sku
        objects["title"] = title
        serializer = DownloadEbayListingSerializer(data=objects)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["products"][0]
        title = objects["products"][0]["title"]

        # Base product update or create
        base_product_defaults = {
            "value": product["value"],
            "currency": product["currency"],
            "title": title,
            "description": listing_description,
            "main_image": main_image,
        }
        base_product, created = BaseProduct.objects.update_or_create(
            user=self.channel.marketplace_user_account.user,
            sku=sku,
            defaults=base_product_defaults,
        )
        base_product.extra_images.set(extra_images)

        # Get payment policy or download first
        payment_policy = self.get_policy(
            policy_id=payment_policy_id,
            model=PaymentPolicy,
            action=RemoteDownloadPaymentPolicy,
            action_key="payment_policy_id",
        )

        # Get fulfillment policy or download first
        fulfillment_policy = self.get_policy(
            policy_id=fulfillment_policy_id,
            model=FulfillmentPolicy,
            action=RemoteDownloadFulfillmentPolicy,
            action_key="fulfillment_policy_id",
        )

        # Get return policy or download first
        return_policy = self.get_policy(
            policy_id=return_policy_id,
            model=ReturnPolicy,
            action=RemoteDownloadReturnPolicy,
            action_key="return_policy_id",
        )

        # Get location or download first
        location = self.get_location(merchant_location_key=merchant_location_key)

        # Create EbayListing
        group_listing_id = objects["groupListingId"]
        serializer_kwargs = {
            "base_product": base_product,
            "channel": self.channel,
            "category": ebay_category,
            "paymentPolicy": payment_policy,
            "returnPolicy": return_policy,
            "fulfillmentPolicy": fulfillment_policy,
            "location": location,
            "groupListingId": group_listing_id,
        }
        instance = serializer.save(**serializer_kwargs)

        # Create message
        message = f"{message}. Листинг {instance}."
        # Return success with data
        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadAllLiveOldStyleListings(
    MigrateEbayOldStyleListings, EbayChannelAction
):
    def download_product(self, **kwargs):
        action = RemoteDownloadEbayListing(instance=self)
        return action(**kwargs)

    def success_trigger(
        self, message: str, objects: dict, newly_migrated_only=False, **kwargs
    ):
        is_success, message, objects = super().success_trigger(
            message, objects, **kwargs
        )

        if newly_migrated_only:
            listing_data_list = objects["results"]["success"]
        else:
            listing_data_list = (
                objects["results"]["success"] + objects["results"]["already_migrated"]
            )
        # filter listings by ebay domain
        listing_data_list = [
            listing_data
            for listing_data in listing_data_list
            if listing_data["domain_code"] == self.channel.domain.code
        ]

        succ_listings = []
        failed_listings = []
        error_messages = {}

        for listing_data in listing_data_list:
            if listing_data["domain_code"] != self.channel.domain.code:
                continue

            is_success, message, objects = self.download_product(
                listingId=listing_data["listingId"]
            )

            if is_success:
                succ_listings.append(listing_data["listingId"])
            else:
                failed_listings.append(listing_data["listingId"])
                error_messages[listing_data["listingId"]] = message

        objects["results"] = {
            "succ_listings": succ_listings,
            "failed_listings": failed_listings,
            "error_messages": error_messages,
        }

        message = "Активные листинги успешно загружены."
        return True, message, objects
