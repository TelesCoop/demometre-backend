from django.utils import timezone
from django.db.models import QuerySet
from rest_framework import mixins, viewsets
from my_auth.utils import get_authenticated_or_anonymous_user_from_request
from my_auth.permissions import IsAuthenticatedOrAnonymous

from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin
from open_democracy_back.models.participation_models import Participation, Response

from open_democracy_back.serializers.participation_serializers import (
    ParticipationSerializer,
    ResponseSerializer,
)


class ParticipationView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticatedOrAnonymous]
    serializer_class = ParticipationSerializer

    def get_queryset(self) -> QuerySet:
        user = get_authenticated_or_anonymous_user_from_request(self.request)
        return Participation.objects.filter(
            user_id=user.id,
            assessment__initialization_date__lt=timezone.now(),
        )


class ResponseView(
    mixins.ListModelMixin, UpdateOrCreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticatedOrAnonymous]
    serializer_class = ResponseSerializer

    def get_queryset(self):
        user = get_authenticated_or_anonymous_user_from_request(self.request)
        query = Response.objects.filter(participation__user_id=user.id)

        context = self.request.query_params.get("context")
        if context:
            is_profiling_question = context == "profiling"
            query = query.filter(question__profiling_question=is_profiling_question)

        participation_id = self.request.query_params.get("participation_id")
        if participation_id:
            query = query.filter(participation_id=participation_id)

        return query

    def get_or_update_object(self, request):
        return self.get_queryset().get(
            participation_id=request.data.get("participation_id"),
            question_id=request.data.get("question_id"),
        )
