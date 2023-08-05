from ebay.account.models import EbayUserAccount
from ebay.category.helpers import get_category_aspects
from ebay.category.models import EbayCategory
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class EbayCategoryAspectViewSet(ViewSet):
    def list(self, request, *args, **kwargs):
        ebay_user_account = None
        ebay_user_account_qs = EbayUserAccount.objects.filter(
            marketplace_user_account__user=self.request.user
        )
        if ebay_user_account_qs.exists():
            ebay_user_account = ebay_user_account_qs.first()
        if ebay_user_account:
            category = EbayCategory.objects.get(id=self.kwargs["category_id"])
            api_kwargs = {"category": category}
            if category.transportSupported:
                api_kwargs[
                    "marketplace_user_account"
                ] = ebay_user_account.marketplace_user_account
            is_success, message, aspects = get_category_aspects(**api_kwargs)
            if is_success:
                return Response(aspects, status.HTTP_200_OK)
        else:
            message = (
                "Для запроса аспектов категорий необходим eBay аккаунт пользователя."
            )
        return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
