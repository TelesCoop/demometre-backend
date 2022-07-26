from rest_framework import mixins, viewsets
from open_democracy_back.models.settings_models import RGPDSettings, StructureSettings

from open_democracy_back.serializers.setting_serializers import (
    RGPDSettingsSerializer,
    StructureSettingsSerializer,
)


class StructureSettingsView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = StructureSettingsSerializer
    queryset = StructureSettings.objects.all()


class RGPDSettingsView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RGPDSettingsSerializer
    queryset = RGPDSettings.objects.all()
