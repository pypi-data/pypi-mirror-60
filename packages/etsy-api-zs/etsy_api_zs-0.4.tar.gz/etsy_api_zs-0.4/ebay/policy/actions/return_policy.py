from ebay.policy.actions import base as base_actions
from ebay.policy.models import ReturnPolicy
from ebay.policy.serializers.return_policy import BaseReturnPolicySerializer
from ebay.policy.serializers.return_policy.remote_api import (
    RemoteDownloadReturnPolicySerializer,
    UpdateOrCreateReturnPolicySerializer,
)
from ebay_api.sell.account import return_policy as policy_api


class GetReturnPolicy(base_actions.GetPolicyAction):
    description = "Получение политики возврата eBay"
    by_name_api_class = policy_api.GetReturnPolicyByName
    by_id_api_class = policy_api.GetReturnPolicy
    path_param_name = "return_policy_id"


class RemoteDownloadReturnPolicy(
    GetReturnPolicy, base_actions.RemoteDownloadPolicyAction
):
    description = "Получение и сохранение политики возврата eBay"
    policy_id_key = "returnPolicyId"
    serializer = BaseReturnPolicySerializer
    unique_name = "return"


class GetReturnPolicyList(base_actions.GetPolicyListAction):
    description = "Получение всех политик возврата с eBay"
    api_class = policy_api.GetReturnPolicies


class RemoteDownloadReturnPolicyList(
    GetReturnPolicyList, base_actions.RemoteDownloadPolicyListAction
):
    description = "Получение и сохранение всех политик возврата eBay"
    objects_data_list_key = "returnPolicies"
    policy_id_key = "returnPolicyId"
    serializer = RemoteDownloadReturnPolicySerializer
    unique_name = "return"


class UploadReturnPolicy(base_actions.UploadPolicyAction):
    description = "Загрузка политики возврата на eBay"
    api_class = policy_api.CreateReturnPolicy
    payload_serializer = UpdateOrCreateReturnPolicySerializer
    entity_model = UpdateOrCreateReturnPolicySerializer.Meta.model
    entity_name = "policy"

    def success_trigger(self, message: str, objects: dict, **kwargs):
        data = objects["results"]
        data["channel"] = self.channel.id
        data["policy_id"] = data.pop("returnPolicyId")
        data["status"] = "published"
        serializer = RemoteDownloadReturnPolicySerializer(
            instance=self.entity, data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().success_trigger(message, objects, **kwargs)


class UpdateReturnPolicy(base_actions.UpdatePolicyAction):
    description = "Обновление политики возврата на eBay"
    path_param = "return_policy_id"
    api_class = policy_api.UpdateReturnPolicy
    payload_serializer = UpdateOrCreateReturnPolicySerializer
    entity_name = "policy"

    def success_trigger(self, message: str, objects: dict, **kwargs):
        self.entity.status = "published"
        self.entity.save()
        return super().success_trigger(message, objects, **kwargs)


class WithdrawReturnPolicy(base_actions.WithdrawPolicyAction):
    description = "Удаление политики возврата с eBay"
    path_param = "return_policy_id"
    api_class = policy_api.DeleteReturnPolicy
    entity_name = "policy"
    entity_model = ReturnPolicy

    def success_trigger(self, message: str, objects: dict, **kwargs):
        self.entity.status = "ready_to_publish"
        self.entity.policy_id = None
        self.entity.save()
        return super().success_trigger(message, objects, **kwargs)
