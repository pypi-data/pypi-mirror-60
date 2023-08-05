from typing import Tuple

from etsy.api.etsy_action import EtsyAccountAction, EtsyEntityAction
from etsy.policy.models import EtsyShippingTemplate
from etsy.policy.serializers.shipping.remote.upload import (
    RemoteCreateEtsyShippingTemplateSerializer,
)
from etsy.policy.serializers.shipping.remote.download import (
    RemoteDownloadEtsyShippingTemplateSerializer,
)
from etsy.policy.actions.shipping_template_entry import (
    RemoteCreateEtsyShippingTemplateEntry,
    RemoteGetEtsyShippingTemplateEntryList,
    RemoteDeleteEtsyShippingTemplateEntry,
)

# BASE


class RemoteGetEtsyShippingTemplateList(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_findallusershippingprofiles
    """

    api_method = "findAllUserShippingProfiles"
    params = ["user_id"]


class RemoteGetEtsyShippingTemplate(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_getshippingtemplate
    """

    api_method = "getShippingTemplate"
    params = ["shipping_template_id"]


class RemoteDeleteEtsyShippingTemplate(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_deleteshippingtemplate
    """

    api_method = "deleteShippingTemplate"
    params = ["shipping_template_id"]


class RemoteCreateEtsyShippingTemplate(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_createshippingtemplate
    """

    api_method = "createShippingTemplate"
    params = [
        # body
        "title",
        "origin_country_id",
        "destination_country_id",
        "primary_cost",
        "secondary_cost",
        "destination_region_id",
        "min_processing_days",
        "max_processing_days",
    ]


class RemoteUpdateEtsyShippingTemplate(EtsyAccountAction):
    """
    Docs:
    https://www.etsy.com/developers/documentation/reference/shippingtemplate#method_updateshippingtemplate
    """

    api_method = "updateShippingTemplate"
    params = [
        "shipping_template_id",
        # body
        "title",
        "origin_country_id",
        "min_processing_days",
        "max_processing_days",
    ]


# CUSTOM


class RemoteDownloadEtsyShippingTemplateList(RemoteGetEtsyShippingTemplateList):
    def get_shipping_template_entries(
        self, shipping_template_id
    ) -> Tuple[bool, str, dict]:
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyShippingTemplateEntryList,
            shipping_template_id=shipping_template_id,
        )
        return objects["results"]

    def success_trigger(self, message: str, objects: dict, **kwargs):
        # Get shipping template entries for each shipping template
        for shipping_template in objects["results"]:
            entries = self.get_shipping_template_entries(
                shipping_template["shipping_template_id"]
            )
            # Format entries
            for entry in entries:
                entry["destination_country"] = entry.pop("destination_country_id", None)
                entry["destination_region"] = entry.pop("destination_region_id", None)
            # Add entries for shipping template
            shipping_template["entries"] = entries
        # Validate shipping templates data
        serializer = RemoteDownloadEtsyShippingTemplateSerializer(
            data=objects["results"], many=True
        )
        serializer.is_valid(raise_exception=True)
        # Save shipping templates
        serializer.save(marketplace_user_account=self.marketplace_user_account)
        return True, "Политики доставки успешно загружены.", {}


class EtsyShippingTemplateAction(EtsyEntityAction):
    entity_model = EtsyShippingTemplate
    entity_name = "shipping_template"


class SyncEtsyShippingTemplateAndEntryList(EtsyShippingTemplateAction):
    def create_or_update_entry(self, entry_data: dict):
        is_success, message, objects = self.raisable_action(
            RemoteCreateEtsyShippingTemplateEntry, **entry_data,
        )
        return objects["results"][0]["shipping_template_entry_id"]

    def delete_entry(self, entry_id: int):
        return self.raisable_action(
            RemoteDeleteEtsyShippingTemplateEntry, shipping_template_entry_id=entry_id,
        )

    def create_template(self, template_data: dict):
        is_success, message, objects = self.raisable_action(
            RemoteCreateEtsyShippingTemplate, **template_data,
        )
        return objects["results"]["shipping_template_id"]

    def update_template(self, template_data: dict):
        is_success, message, objects = self.raisable_action(
            RemoteUpdateEtsyShippingTemplate, **template_data,
        )
        print(objects)
        return objects["results"]["shipping_template_id"]

    def delete_template(self, shipping_template_id):
        return self.raisable_action(
            RemoteDeleteEtsyShippingTemplate, shipping_template_id=shipping_template_id,
        )

    def make_request(self, **kwargs):
        data = RemoteCreateEtsyShippingTemplateSerializer(self.shipping_template).data

        try:
            # create or update shipping template on Etsy
            if self.shipping_template.published:
                # case: shipping template is already uploaded
                template_data = {
                    **data,
                    'shipping_template_id': self.shipping_template.shipping_template_id,
                }
                entries_data = data.pop("entries")
                self.shipping_template_id = self.update_template(template_data)
            else:
                # case: shipping template is not uploaded
                entries_data = data.pop("entries")
                template_data = {**data, **entries_data[0]}
                entries_data = entries_data[1:]
                self.shipping_template_id = self.create_template(template_data)
                # mark template as published and save id
                self.shipping_template.shipping_template_id = self.shipping_template_id
                self.shipping_template.published = True
                self.shipping_template.save()

            # sync entries
            for entry_data in entries_data:
                # TODO: delete if is_removed == True
                entry_data.update({"shipping_template_id": self.shipping_template_id})
                self.create_or_update_entry(entry_data)

        except self.exception_class as error:
            # # delete template from etsy and mark it as unpublished
            # if getattr(self, "shipping_template_id", None):
            #     self.delete_template(self.shipping_template_id)
            # self.shipping_template.published = False

            is_success = False
            message = (
                "Не удалось синхронизировать политику доставки с Etsy "
                f"(название: {self.shipping_template.title[:30]}).\n{error}"
            )
            objects = {"response": getattr(error, "response", None)}

        else:
            is_success = True
            message = (
                "Политика доставки успешно синхронизирована с Etsy "
                f"(название: {self.shipping_template.title[:30]})."
            )
            objects = {"shipping_template_id": self.shipping_template_id}

        return is_success, message, objects
