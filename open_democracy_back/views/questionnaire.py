from rest_framework import mixins, viewsets

from open_democracy_back.models.questionnaire import (
    Criteria,
    Marker,
    Pillar,
    ProfilingQuestion,
    QuestionnaireQuestion,
)
from open_democracy_back.serializers.questionnaire import (
    CriteriaSerializer,
    MarkerSerializer,
    PillarSerializer,
    ProfilingQuestionSerializer,
    QuestionnaireQuestionSerializer,
)


class PillarView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PillarSerializer
    queryset = Pillar.objects.all()


class MarkerView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MarkerSerializer
    queryset = Marker.objects.all()


class CriteriaView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CriteriaSerializer
    queryset = Criteria.objects.all()


class QuestionnaireQuestionView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = QuestionnaireQuestionSerializer
    queryset = QuestionnaireQuestion.objects.all()


class ProfilingQuestionView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProfilingQuestionSerializer
    queryset = ProfilingQuestion.objects.all()
