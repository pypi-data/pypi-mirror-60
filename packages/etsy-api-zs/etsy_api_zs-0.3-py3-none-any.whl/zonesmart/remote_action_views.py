from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from zonesmart.marketplace.api.marketplace_action import MarketplaceAction


class RemoteActionResponseViewSet(ViewSetMixin, GenericAPIView):
    remote_api_actions = {}

    def get_api_action(self, **kwargs) -> MarketplaceAction:
        api_action = self.remote_api_actions.get(self.action)
        return api_action(**kwargs)

    def get_action_response(
        self,
        detail: bool = True,
        entity=None,
        ignore_status: bool = False,
        required_statuses: list = None,
        action_init_kwargs: dict = None,
        action_call_kwargs: dict = None,
    ) -> Response:
        if action_init_kwargs is None:
            action_init_kwargs = {}
        if action_call_kwargs is None:
            action_call_kwargs = {}

        if detail:
            if not entity:
                entity = self.get_object()

            if not ignore_status:
                assert (
                    required_statuses
                ), "You should specify entity status for detail action response."
                entity_status = getattr(entity, "status", None)
                if entity_status and entity_status not in required_statuses:
                    message = (
                        f"You cannot call {self.action} action when entity status is {entity_status}. "
                        f'Required entity statuses for action are: {", ".join(required_statuses)}.'
                    )
                    return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

            action_init_kwargs.update({"entity": entity})

        api_action = self.get_api_action(**action_init_kwargs)
        is_success, message, objects = api_action(**action_call_kwargs)

        if is_success:
            return Response(data=message, status=status.HTTP_201_CREATED)

        return Response(data=message, status=status.HTTP_400_BAD_REQUEST)


class RemoteDownloadListActionByChannel(RemoteActionResponseViewSet):
    @action(
        detail=False,
        methods=["GET"],
        url_path=r"remote_download_list/(?P<channel_id>[^/.]+)",
    )
    def remote_download_list(self, request, *args, **kwargs) -> Response:
        action_init_kwargs = {"channel_id": kwargs["channel_id"]}
        return self.get_action_response(
            detail=False, action_init_kwargs=action_init_kwargs
        )


class RemoteDownloadListActionByMarketplaceAccount(RemoteActionResponseViewSet):
    @action(
        detail=False,
        methods=["GET"],
        url_path=r"remote_download_list/(?P<marketplace_user_account_id>[^/.]+)",
    )
    def remote_download_list(self, request, *args, **kwargs) -> Response:
        action_init_kwargs = {
            "marketplace_user_account_id": kwargs["marketplace_user_account_id"]
        }
        return self.get_action_response(
            detail=False, action_init_kwargs=action_init_kwargs
        )


class RemoteCreateAction(RemoteActionResponseViewSet):
    @action(detail=True, methods=["POST"])
    def remote_create(self, request, *args, **kwargs) -> Response:
        return self.get_action_response(required_statuses=["ready_to_publish"])


class RemoteDeleteAction(RemoteActionResponseViewSet):
    @action(detail=True, methods=["DELETE"])
    def remote_delete(self, request, *args, **kwargs) -> Response:
        return self.get_action_response(
            required_statuses=["published", "update_required"]
        )


class RemoteUpdateAction(RemoteActionResponseViewSet):
    @action(detail=True, methods=["PUT"])
    def remote_update(self, request, *args, **kwargs) -> Response:
        return self.get_action_response(required_statuses=["update_required"])


class RemoteSyncAction(RemoteActionResponseViewSet):
    @action(detail=True, methods=["POST"])
    def remote_sync(self, request, *args, **kwargs) -> Response:
        return self.get_action_response(
            required_statuses=["update_required", "ready_to_publish"],
        )
