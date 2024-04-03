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
    queryset = (
        Pillar.objects.prefetch_related("markers")
        .prefetch_related("markers__criterias")
        .prefetch_related("markers__criterias__questions")
        .prefetch_related("markers__criterias__thematic_tags")
        .prefetch_related("markers__criterias__related_definition_ordered")
        .prefetch_related("markers__criterias")
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

    def get_queryset(self):
        return (
            QuestionnaireQuestion.objects.exclude(criteria__marker__pillar__isnull=True)
            .prefetch_related("profiles")
            .prefetch_related("criteria")
            .prefetch_related("criteria__marker")
            .prefetch_related("criteria__marker__pillar")
            .prefetch_related("criteria__marker__pillar__survey")
            .prefetch_related("allows_to_explain")
            .prefetch_related("assessment_types")
            .prefetch_related("response_choices")
            .prefetch_related("categories")
            .prefetch_related("roles")
            .prefetch_related("rules")
            .prefetch_related("explained_by")
            .order_by(
                "criteria__marker__pillar__code",
                "criteria__marker__code",
                "criteria__code",
                "code",
            )
        )


class DefinitionView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Definition.objects.all()
    serializer_class = DefinitionSerializer
