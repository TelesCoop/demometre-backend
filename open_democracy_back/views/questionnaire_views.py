from rest_framework import mixins, viewsets

from open_democracy_back.models.questionnaire_and_profiling_models import (
    Criteria,
    Marker,
    Pillar,
    QuestionnaireQuestion,
    Definition,
)
from open_democracy_back.serializers.questionnaire_and_profiling_serializers import (
    CriteriaSerializer,
    MarkerSerializer,
    PillarSerializer,
    QuestionnaireQuestionSerializer,
    FullPillarSerializer,
    DefinitionSerializer,
)


class QuestionnaireStructureView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FullPillarSerializer
    queryset = Pillar.objects.all()


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
    ordering = (
        "code",
        "criteria__code",
        "criteria__marker__code",
        "criteria__marker__pillar__code",
    )

    def get_queryset(self):
        return QuestionnaireQuestion.objects.exclude(
            criteria__marker__pillar__isnull=True
        )


class DefinitionView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Definition.objects.all()
    serializer_class = DefinitionSerializer
