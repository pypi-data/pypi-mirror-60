from ebay.policy.actions import base as base_actions
from ebay.policy.serializers.payment_policy.remote_api import (
    RemoteDownloadPaymentPolicySerializer,
    UpdateOrCreatePaymentPolicySerializer,
)
from ebay_api.sell.account import payment_policy as policy_api


class GetPaymentPolicy(base_actions.GetPolicyAction):
    description = "Получение политики оплаты eBay"
    by_name_api_class = policy_api.GetPaymentPolicyByName
    by_id_api_class = policy_api.GetPaymentPolicy
    path_param_name = "payment_policy_id"


class RemoteDownloadPaymentPolicy(
    GetPaymentPolicy, base_actions.RemoteDownloadPolicyAction
):
    description = "Получение и сохранение политики оплаты eBay"
    policy_id_key = "paymentPolicyId"
    serializer = RemoteDownloadPaymentPolicySerializer
    unique_name = "payment"


class GetPaymentPolicyList(base_actions.GetPolicyListAction):
    description = "Получение всех политик оплаты с eBay"
    api_class = policy_api.GetPaymentPolicies


class RemoteDownloadPaymentPolicyList(
    GetPaymentPolicyList, base_actions.RemoteDownloadPolicyListAction
):
    description = "Получение и сохранение всех политик оплаты eBay"
    objects_data_list_key = "paymentPolicies"
    policy_id_key = "paymentPolicyId"
    serializer = RemoteDownloadPaymentPolicySerializer
    unique_name = "payment"


class UploadPaymentPolicy(base_actions.UploadPolicyAction):
    description = "Загрузка политики оплаты на eBay"
    api_class = policy_api.CreatePaymentPolicy
    payload_serializer = UpdateOrCreatePaymentPolicySerializer
    entity_model = UpdateOrCreatePaymentPolicySerializer.Meta.model
    entity_name = "policy"

    def success_trigger(self, message: str, objects: dict, **kwargs):
        data = objects["results"]
        data["channel"] = self.channel.id
        data["policy_id"] = data.pop("paymentPolicyId")
        data["status"] = "published"
        serializer = RemoteDownloadPaymentPolicySerializer(
            instance=self.entity, data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().success_trigger(message, objects, **kwargs)


class UpdatePaymentPolicy(base_actions.UpdatePolicyAction):
    description = "Обновление политики оплаты на eBay"
    path_param = "payment_policy_id"
    api_class = policy_api.UpdatePaymentPolicy
    payload_serializer = UpdateOrCreatePaymentPolicySerializer
    entity_name = "policy"

    def success_trigger(self, message: str, objects: dict, **kwargs):
        self.entity.status = "published"
        self.entity.save()
        return super().success_trigger(message, objects, **kwargs)


class WithdrawPaymentPolicy(base_actions.WithdrawPolicyAction):
    description = "Удаление политики оплаты с eBay"
    path_param = "payment_policy_id"
    api_class = policy_api.DeletePaymentPolicy
    entity_name = "policy"
    entity_model = UpdateOrCreatePaymentPolicySerializer.Meta.model

    def success_trigger(self, message: str, objects: dict, **kwargs):
        self.entity.status = "ready_to_publish"
        self.entity.policy_id = None
        self.entity.save()
        return super().success_trigger(message, objects, **kwargs)
