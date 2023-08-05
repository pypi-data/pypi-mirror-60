from django.db.models import QuerySet

from rest_framework import viewsets
from rest_framework.serializers import Serializer


class GenericSerializerViewSet(viewsets.GenericViewSet):
    serializer_classes = {}
    lookup_field = "id"

    def get_serializer_class(self) -> Serializer:
        return self.serializer_classes.get(
            self.action, self.serializer_classes.get("default", self.serializer_class)
        )

    def get_queryset(self) -> QuerySet:
        return self.get_serializer_class().Meta.model.objects.all()


class GenericSerializerModelViewSet(GenericSerializerViewSet, viewsets.ModelViewSet):
    pass
