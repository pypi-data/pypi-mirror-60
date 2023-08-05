from django.db import IntegrityError

from ebay.api.ebay_action import EbayAccountAction, EbayEntityAction
from ebay.location.models import EbayLocation
from ebay.location.serializers import BaseEbayLocationSerializer
from ebay.location.serializers.api.helpers import nested_location_to_flat
from ebay.location.serializers.api.nested import EbayLocationNestedSerializer
from ebay.location.serializers.api.update import UpdateEbayLocationSerializer
from ebay_api.sell.inventory import location as location_api
from rest_framework.exceptions import ValidationError


class EbayLocationAction(EbayEntityAction):
    description = "Действие со складом eBay"
    entity_name = "location"
    entity_model = EbayLocation

    def get_path_params(self, **kwargs):
        kwargs["merchantLocationKey"] = self.entity.merchantLocationKey
        return super().get_path_params(**kwargs)


class RemoteUploadEbayLocation(EbayLocationAction):
    description = "Добавление склада на eBay"
    api_class = location_api.CreateInventoryLocation
    payload_serializer = EbayLocationNestedSerializer

    def success_trigger(self, message: str, objects: dict, *args, **kwargs):
        self.entity.status = self.entity.STATUS.published
        self.entity.save()
        return super().success_trigger(message=message, objects=objects)


class RemoteUpdateEbayLocation(EbayLocationAction):
    description = "Обновление склада на eBay"
    api_class = location_api.UpdateInventoryLocation
    payload_serializer = UpdateEbayLocationSerializer

    def success_trigger(self, message: str, objects: dict, **kwargs):
        self.entity.status = self.entity.STATUS.published
        self.entity.save()
        return super().success_trigger(message=message, objects=objects)


class WithdrawEbayLocation(EbayLocationAction):
    description = "Удаление склада с eBay"
    api_class = location_api.DeleteInventoryLocation

    def success_trigger(self, message: str, objects: dict, *args, **kwargs):
        self.entity.published = False
        self.entity.save()
        return super().success_trigger(message=message, objects=objects)


class WithdrawEbayLocationByKey(EbayAccountAction):
    description = "Удаление склада с eBay по ключу"
    api_class = location_api.DeleteInventoryLocation


class RemoteGetEbayLocation(EbayAccountAction):
    description = "Загрузка склада с eBay"
    api_class = location_api.GetInventoryLocation


class RemoteDownloadEbayLocation(RemoteGetEbayLocation):
    description = "Получение и сохранение склада с eBay"

    def success_trigger(self, message: str, objects: dict, **kwargs):
        location_data = nested_location_to_flat(objects["results"])
        location_data[
            "unique_marketplace_user_account"
        ] = self.marketplace_user_account.id
        location_data["status"] = BaseEbayLocationSerializer.Meta.model.STATUS.published

        serializer = BaseEbayLocationSerializer(data=location_data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError as e:
            error_args = str(e.args)
            if "unique_unique_marketplace_user_account" in error_args:
                raise ValidationError("Склад был загружен ранее")

        return super().success_trigger(message=message, objects=objects)


class RemoteGetEbayLocations(EbayAccountAction):
    description = "Загрузка всех складов с eBay"
    api_class = location_api.GetInventoryLocations
    next_token_action = True

    def success_trigger(self, message, objects, **kwargs):
        locations_data = {"total": 0, "locations": []}
        for location_data in objects["results"]:
            locations_data["total"] += location_data["total"]
            locations_data["locations"] += location_data["locations"]
        objects["results"] = locations_data
        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadEbayLocations(RemoteGetEbayLocations):
    description = "Загрузка и сохранение всех складов с eBay"

    def success_trigger(self, message: str, objects: dict, **kwargs):
        is_success, message, objects = super().success_trigger(
            message, objects, **kwargs
        )
        location_list_data = objects["results"]["locations"]

        for location_data in location_list_data:
            location_data = nested_location_to_flat(location_data)
            location_data["marketplace_user_account"] = self.marketplace_user_account.id
            location_data[
                "status"
            ] = BaseEbayLocationSerializer.Meta.model.STATUS.published

        serializer = BaseEbayLocationSerializer(data=location_list_data, many=True)
        serializer.is_valid(raise_exception=True)
        # Try to save and handle UniqueConstraint model errors
        try:
            serializer.save()
        except IntegrityError as e:
            error_args = str(e.args)
            message = error_args
            # if 'unique_Channel' in error_args:
            #     raise ValidationError('Склад был загружен ранее')

        return is_success, message, objects
