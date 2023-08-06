from ebay.policy.actions import base as base_actions
from ebay.policy.serializers.fulfillment_policy.remote_api import (
    RemoteDownloadFulfillmentPolicySerializer,
    UpdateOrCreateFulfillmentPolicySerializer,
)
from ebay_api.sell.account import fulfillment_policy as policy_api


class GetFulfillmentPolicy(base_actions.GetPolicyAction):
    description = "Получение политики фулфилмента eBay"
    by_name_api_class = policy_api.GetFulfillmentPolicyByName
    by_id_api_class = policy_api.GetFulfillmentPolicy
    path_param_name = "fulfillment_policy_id"


class RemoteDownloadFulfillmentPolicy(
    GetFulfillmentPolicy, base_actions.RemoteDownloadPolicyAction
):
    description = "Получение и сохранение политики фулфилмента eBay"
    policy_id_key = "fulfillmentPolicyId"
    serializer = RemoteDownloadFulfillmentPolicySerializer
    unique_name = "fulfillment"


class GetFulfillmentPolicyList(base_actions.GetPolicyListAction):
    description = "Получение всех политик фулфилмента с eBay"
    api_class = policy_api.GetFulfillmentPolicies


class RemoteDownloadFulfillmentPolicyList(
    GetFulfillmentPolicyList, base_actions.RemoteDownloadPolicyListAction
):
    description = "Получение и сохранение всех политик фулфилмента eBay"
    objects_data_list_key = "fulfillmentPolicies"
    policy_id_key = "fulfillmentPolicyId"
    serializer = RemoteDownloadFulfillmentPolicySerializer
    unique_name = "fulfillment"


class UploadFulfillmentPolicy(base_actions.UploadPolicyAction):
    description = "Загрузка политики фулфилмента на eBay"
    api_class = policy_api.CreateFulfillmentPolicy
    payload_serializer = UpdateOrCreateFulfillmentPolicySerializer
    entity_model = UpdateOrCreateFulfillmentPolicySerializer.Meta.model
    entity_name = "policy"

    def success_trigger(self, message: str, objects: dict, **kwargs):
        data = objects["results"]
        data["channel"] = self.channel.id
        data["policy_id"] = data.pop("fulfillmentPolicyId")
        data["status"] = "published"
        serializer = RemoteDownloadFulfillmentPolicySerializer(
            instance=self.entity, data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().success_trigger(message, objects, **kwargs)


class UpdateFulfillmentPolicy(base_actions.UpdatePolicyAction):
    description = "Обновление политики фулфилмента на eBay"
    path_param = "fulfillment_policy_id"
    api_class = policy_api.UpdateFulfillmentPolicy
    payload_serializer = UpdateOrCreateFulfillmentPolicySerializer
    entity_name = "policy"
    entity_model = RemoteDownloadFulfillmentPolicySerializer.Meta.model

    def success_trigger(self, message: str, objects: dict, **kwargs):
        self.entity.status = "published"
        self.entity.save()
        return super().success_trigger(message, objects, **kwargs)


class WithdrawFulfillmentPolicy(base_actions.WithdrawPolicyAction):
    description = "Удаление политики фулфилмента с eBay"
    path_param = "fulfillment_policy_id"
    api_class = policy_api.DeleteFulfillmentPolicy
    entity_name = "policy"
    entity_model = RemoteDownloadFulfillmentPolicySerializer.Meta.model

    def success_trigger(self, message: str, objects: dict, **kwargs):
        self.entity.status = "ready_to_publish"
        self.entity.policy_id = None
        self.entity.save()
        return super().success_trigger(message, objects, **kwargs)
