from ebay.category.filters import EbayCategoryFilter
from ebay.category.helpers import get_properties, get_property_values
from ebay.category.models import EbayCategory
from ebay.category.serializers.base import EbayCategorySerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class EbayCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly category model ViewSet
    """

    serializer_class = EbayCategorySerializer
    queryset = EbayCategory.objects.all()
    filterset_class = EbayCategoryFilter
    lookup_field = "id"

    def get_queryset(self):
        qs = super().get_queryset()
        # Specify qs for compatibility property action
        if self.action in ["compatibility_property", "compatibility_property_value"]:
            # Filter qs by transportSupported field
            qs = qs.filter(transportSupported=True)
            # Check if category id is in qs and raise validation error if not
            category_id = self.kwargs["id"]
            if not qs.filter(id=category_id).exists():
                raise ValidationError(
                    {"id": f"Категория с id {category_id} не поддерживает транспорт."}
                )
        return qs

    @action(detail=True, methods=["GET"])
    def compatibility_property(self, request, *args, **kwargs):
        is_success, message, property_list = get_properties(category=self.get_object())
        if is_success:
            return Response(data=property_list, status=status.HTTP_200_OK)
        return Response(data=message, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=["GET"], url_path=r"compatibility_property/(?P<name>[\w]+)"
    )
    def compatibility_property_value(self, request, *args, **kwargs):
        is_success, message, property_values = get_property_values(
            category=self.get_object(),
            name=kwargs["name"],
            filter_query=request.GET["filter_query"],
        )
        if is_success:
            return Response(data=property_values, status=status.HTTP_200_OK)
        return Response(data=message, status=status.HTTP_400_BAD_REQUEST)
