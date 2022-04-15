from django.utils import timezone
from django.db.models import QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin
from open_democracy_back.models.participation_models import Participation, Response

from open_democracy_back.serializers.participation_serializers import (
    ParticipationSerializer,
    ResponseSerializer,
)


class ParticipationsView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = ParticipationSerializer
    queryset = Participation.objects.all()


class ParticipationView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = ParticipationSerializer
    queryset = Participation.objects.all()


class UserParticipationView(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ParticipationSerializer

    def get_queryset(self) -> QuerySet:
        return Participation.objects.filter(
            user_id=self.kwargs.get("user_pk"),
            assessment__initialization_date__lt=timezone.now(),
        )


class ResponseView(
    mixins.ListModelMixin, UpdateOrCreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    serializer_class = ResponseSerializer
    queryset = Response.objects.all()

    def get_or_update_object(self, request):
        return self.get_queryset().get(
            participation_id=request.data.get("participation_id"),
            question_id=request.data.get("question_id"),
        )
