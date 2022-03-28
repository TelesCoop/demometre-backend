from rest_framework import mixins, viewsets
from open_democracy_back.models.participation_models import Participation

from open_democracy_back.serializers.participation_serializers import (
    ParticipationSerializer,
)


class ParticipationView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ParticipationSerializer
    queryset = Participation.objects.all()
