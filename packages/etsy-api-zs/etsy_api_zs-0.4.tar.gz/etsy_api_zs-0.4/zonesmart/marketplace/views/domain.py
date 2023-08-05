from rest_framework import viewsets

from zonesmart.marketplace.serializers.domain import DomainSerializer


class DomainReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DomainSerializer
    lookup_field = "id"

    def get_queryset(self):
        return DomainSerializer.Meta.model.objects.filter(
            marketplace_id=self.kwargs["marketplace_id"]
        )
