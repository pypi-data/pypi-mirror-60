from django.core.cache import cache

from etsy.account.models import EtsyUserAccount
from etsy.account.serializers import (
    CreateEtsyUserAccountSerializer,
    EtsyUserAccountSerializer,
)
from etsy.api.etsy_access import EtsyAPIAccess, EtsyAPIAccessError
from etsy.account.actions import RemoteDownloadEtsyShopsAndSections
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from zonesmart.marketplace.models import (
    Channel,
    Domain,
    Marketplace,
    MarketplaceUserAccount,
)
from zonesmart.views import GenericSerializerViewSet


class EtsyUserAccountViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericSerializerViewSet,
):
    serializer_classes = {
        "default": EtsyUserAccountSerializer,
        "create": CreateEtsyUserAccountSerializer,
    }

    def get_queryset(self):
        return (
            super()
            .get_serializer_class()
            .Meta.model.objects.filter(marketplace_user_account__user=self.request.user)
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        temp_access_token = serializer.validated_data["oauth_token"]
        oauth_verifier = serializer.validated_data["oauth_verifier"]
        # save secret token key from cache
        temp_access_token_secret = cache.get(temp_access_token)
        cache.expire(temp_access_token, timeout=0)

        api = EtsyAPIAccess()
        try:
            token = api.get_user_token_data(
                oauth_verifier=oauth_verifier,
                temp_access_token=temp_access_token,
                temp_access_token_secret=temp_access_token_secret,
            )
        except EtsyAPIAccessError as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

        marketplace_user_account = MarketplaceUserAccount.objects.create(
            user=self.request.user,
            marketplace=Marketplace.objects.get(unique_name="etsy"),
        )
        etsy_account, created = EtsyUserAccount.objects.update_or_create(
            marketplace_user_account=marketplace_user_account,
            sandbox=api.is_sandbox,
            defaults={"access_token": token.key, "access_token_secret": token.secret,},
        )

        # Create the only channel
        channel, created = Channel.objects.update_or_create(
            marketplace_user_account=marketplace_user_account,
            domain=Domain.objects.get(code="ETSY"),
            defaults={"name": "Канал продаж Etsy"},
        )

        # Download user shops and shop sections
        action = RemoteDownloadEtsyShopsAndSections(
            marketplace_user_account=marketplace_user_account
        )
        is_success, message, objects = action()

        if not is_success:
            return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class EtsyUserAccountAuthUrl(APIView):
    def get(self, request, *args, **kwargs):
        api = EtsyAPIAccess()
        try:
            temp_token = api.get_temp_token()
        except EtsyAPIAccessError as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

        temp_access_token = temp_token.key
        temp_access_token_secret = temp_token.secret
        # save secret token key in cache
        cache.set(temp_access_token, temp_access_token_secret, timeout=600)

        url = api.get_auth_url(temp_access_token=temp_access_token)
        return Response(url)
