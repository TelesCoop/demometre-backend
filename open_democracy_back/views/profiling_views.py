from django.db.models import QuerySet
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from open_democracy_back.models.participation_models import Participation

from open_democracy_back.models.questionnaire_and_profiling_models import (
    ProfilingQuestion,
    Role,
)
from open_democracy_back.serializers.questionnaire_and_profiling_serializers import (
    ProfilingQuestionSerializer,
    RoleSerializer,
)


class ProfilingQuestionView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProfilingQuestionSerializer


class ParticipationProfilingQuestionView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfilingQuestionSerializer

    def get_queryset(self) -> QuerySet:
        participation = Participation.objects.get(
            id=self.kwargs.get("participation_pk")
        )
        population = participation.assessment.population
        return ProfilingQuestion.objects.filter_by_role_and_population(
            participation.role, population
        )


class RoleView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()
