import json
from abc import abstractmethod
from uuid import UUID

from zonesmart.marketplace.api.marketplace_access import MarketplaceAPIAccess
from zonesmart.utils.logger import get_logger

logger = get_logger(app_name=__file__)


class MarketplaceActionError(Exception):
    response = None


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class MarketplaceAction(MarketplaceAPIAccess):
    description = "Действие с маркетплейсом"
    exception_class = MarketplaceActionError

    def __init__(self, raise_exception=False, **kwargs):
        self.raise_exception = raise_exception
        super().__init__(**kwargs)

    @staticmethod
    def get_payload(serializer, instance=None, queryset=None, to_json=True):
        if instance:
            payload = serializer(instance=instance).data
        elif queryset:
            payload = serializer(queryset=queryset, many=True).data
        else:
            raise AttributeError(
                "Сериализатору необходимо передать instance или queryset."
            )

        logger.debug(f"Payload:\n{json.dumps(payload, indent=4, cls=CustomEncoder)}")

        if to_json:
            payload = json.dumps(payload, cls=CustomEncoder)
        return payload

    def __call__(self, **kwargs):
        self.before_request(**kwargs)
        is_success, message, objects = self.make_request(**kwargs)
        self.after_request(is_success, message, objects, **kwargs)

        if is_success:
            is_success, message, objects = self.success_trigger(
                message, objects, **kwargs
            )
            logger.info(message)
        else:
            is_success, message, objects = self.failure_trigger(
                message, objects, **kwargs
            )
            logger.error(message)

        return is_success, message, objects

    @abstractmethod
    def make_request(self, **kwargs):
        pass

    def before_request(self, **kwargs):
        pass

    def after_request(self, is_success, message, objects, **kwargs):
        pass

    def success_trigger(self, message: str, objects: dict, **kwargs):
        return True, message, objects

    def failure_trigger(self, message: str, objects: dict, **kwargs):
        if kwargs.get("raise_exception", False) or getattr(
            self, "raise_exception", False
        ):
            exception = getattr(self, "exception_class", MarketplaceActionError)
            exception.response = objects
            raise exception(message)
        return False, message, objects

    def raisable_action(self, api_class, payload=None, **kwargs):
        action = api_class(instance=self)

        if not isinstance(payload, str):
            payload = json.dumps(payload)

        is_success, message, objects = action(payload=payload, **kwargs)

        if not is_success:
            error = self.exception_class(message)
            error.response = objects.get("response", None)
            raise error

        return is_success, message, objects


class MarketplaceAccountAction(MarketplaceAction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.marketplace_user_account:
            raise AttributeError(
                "Необходимо задать либо marketplace_user_account, либо marketplace_user_account_id."
            )


class MarketplaceChannelAction(MarketplaceAction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.channel:
            raise AttributeError("Необходимо задать либо channel, либо channel_id.")


class MarketplaceEntityAction(MarketplaceAction):
    def __init__(self, instance=None, **kwargs):
        if instance:
            self.entity = instance.entity
            setattr(self, instance.entity_name, self.entity)
        else:
            self.entity = self.set_entity(**kwargs)
            setattr(self, self.entity_name, self.entity)

        super().__init__(**kwargs)

        if (not self.marketplace_user_account) and (not self.channel):
            raise AttributeError(
                "У заданной сущности eBay не заданы ни канал продаж, ни аккаунт маркетплейса."
            )

    @property
    @abstractmethod
    def entity_model(self):
        pass

    @property
    @abstractmethod
    def entity_name(self):
        pass

    def set_entity(self, **kwargs):
        entity = kwargs.get("entity", kwargs.get(self.entity_name))
        entity_id = kwargs.get("entity_id", kwargs.get(f"{self.entity_name}_id"))

        if bool(entity) == bool(entity_id):
            raise AttributeError("Необходимо задать либо entity, либо entity_id.")
        elif entity:
            return entity
        elif entity_id:
            return self.entity_model.objects.get(id=entity_id)

    def set_channel(self, **kwargs):
        entity_channel = getattr(self.entity, "channel", None)
        return super().set_channel(channel=entity_channel)

    def set_marketplace_user_account(self, **kwargs):
        entity_account = getattr(self.entity, "marketplace_user_account", None)
        return super().set_marketplace_user_account(
            marketplace_user_account=entity_account
        )
