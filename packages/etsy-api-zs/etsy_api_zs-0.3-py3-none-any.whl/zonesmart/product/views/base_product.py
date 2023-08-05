from rest_framework.viewsets import ModelViewSet

from zonesmart.product.serializers import BaseProductSerializer
from zonesmart.product.views import ProductActions


class BaseProductViewSet(ModelViewSet, ProductActions):
    """
    ViewSet for BaseProduct model
    """

    serializer_class = BaseProductSerializer

    def get_queryset(self):
        return self.request.user.base_products.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
