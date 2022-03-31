# from django.db.models import QuerySet
from rest_framework import mixins, viewsets

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
    queryset = ProfilingQuestion.objects.all()


class ParticipationProfilingQuestionView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProfilingQuestionSerializer
    queryset = ProfilingQuestion.objects.all()

    # def get_queryset(self) -> QuerySet:
    #     role = self.kwargs.get("participation_pk")
    # return ProfilingQuestion.objects.filter(
    #      question_filters__ = role
    #     ),
    # )


class RoleView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()
