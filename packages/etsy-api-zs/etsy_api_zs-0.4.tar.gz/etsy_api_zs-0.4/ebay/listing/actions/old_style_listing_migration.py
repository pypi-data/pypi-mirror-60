import json

from ebay.api.ebay_action import EbayAccountAction
from ebay.listing.actions.old_style_listing import GetEbayOldStyleListingIds
from ebay_api.sell.inventory.listing import BulkMigrateListing


class MigrateEbayOldStyleListingsBatch(EbayAccountAction):
    # https://developer.ebay.com/api-docs/sell/inventory/resources/listing/methods/bulkMigrateListing
    api_class = BulkMigrateListing

    def make_request(self, listing_ids_batch: list, **kwargs):
        if len(listing_ids_batch) > 5:
            raise ValueError(
                "Размер массива ID листингов не должен превышать пяти элементов."
            )

        payload = json.dumps(
            {"requests": [{"listingId": listingId} for listingId in listing_ids_batch]}
        )
        kwargs["payload"] = payload

        is_success, message, objects = super().make_request(**kwargs)

        if "responses" in objects:
            is_success = True
            objects["results"] = objects.pop("responses")
        elif "responses" in objects.get("results", {}):
            is_success = True
            objects["results"] = objects["results"].pop("responses")

        return is_success, message, objects

    def success_trigger(self, message, objects, listing_ids_batch, **kwargs):
        message = (
            f"Пакет листингов успешно мигрирован.\nID листингов: {listing_ids_batch}."
        )
        return super().success_trigger(message, objects, **kwargs)

    def failure_trigger(self, message, objects, listing_ids_batch, **kwargs):
        message = f"Не удалось мигрировать пакет листингов.\nID листингов: {listing_ids_batch}."
        objects["results"] = [
            {
                "listingId": listingId,
                "statusCode": 500,
                "errors": objects.get("errors", []),
            }
            for listingId in listing_ids_batch
        ]
        return True, message, objects


class MigrateEbayOldStyleListings(EbayAccountAction):
    batch_size = 5

    def download_listings_batch(self, listing_ids_batch: list):
        is_success, message, objects = self.raisable_action(
            api_class=MigrateEbayOldStyleListingsBatch,
            listing_ids_batch=listing_ids_batch,
        )
        return objects["results"]

    def make_request(self, listing_ids: list = None, **kwargs):
        if not listing_ids:
            is_success, message, objects = GetEbayOldStyleListingIds(instance=self)(
                ids_only=True
            )
            listing_ids = objects["results"]

        results = []
        for i in range((len(listing_ids) // self.batch_size) + 1):
            listing_ids_batch = listing_ids[
                i * self.batch_size : min((i + 1) * self.batch_size, len(listing_ids))
            ]
            if not listing_ids_batch:
                break
            results += self.download_listings_batch(listing_ids_batch=listing_ids_batch)

        message = "Миграция листингов завершена."
        objects = {"results": results}
        return True, message, objects

    def success_trigger(self, message: str, objects: dict, **kwargs):
        results = {
            "success": [],
            "fail": [],
            "already_migrated": [],
        }

        for result in objects["results"]:
            status_code = result["statusCode"]
            listingId = result["listingId"]
            if status_code == 409:
                results["already_migrated"].append(
                    {"listingId": listingId, "domain_code": result["marketplaceId"],}
                )
            elif status_code == 200:
                results["success"].append(
                    {
                        "listingId": listingId,
                        "domain_code": result["marketplaceId"],
                        "inventoryItems": result["inventoryItems"],
                        "inventoryItemGroupKey": result.get(
                            "inventoryItemGroupKey", None
                        ),
                    }
                )
            else:
                results["fail"].append(
                    {
                        "listingId": listingId,
                        "statusCode": status_code,
                        "errors": [error["message"] for error in result["errors"]],
                    }
                )

        objects["results"] = results
        return super().success_trigger(message, objects, **kwargs)
