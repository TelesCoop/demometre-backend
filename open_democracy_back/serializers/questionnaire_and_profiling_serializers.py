from rest_framework import serializers

from open_democracy_back.models.questionnaire_and_profiling_models import (
    Criteria,
    Marker,
    Pillar,
    ProfilingQuestion,
    QuestionnaireQuestion,
    ResponseChoice,
    Definition,
)

QUESTION_FIELDS = [
    "id",
    "concatenated_code",
    "name",
    "question_statement",
    "description",
    "type",
    "response_choices",
    "min",
    "max",
    "min_label",
    "max_label",
    "legal_frame",
    "use_case",
    "resources",
]
REFERENTIAL_FIELDS = [
    "description",
    "score_1",
    "score_2",
    "score_3",
    "score_4",
]


class DefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Definition
        fields = ["id", "word", "explanation"]
        read_only_fields = fields


class ResponseChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseChoice
        fields = ["id", "response_choice", "description"]
        read_only_fields = fields


class QuestionnaireQuestionSerializer(serializers.ModelSerializer):
    response_choices = ResponseChoiceSerializer(many=True, read_only=True)
    definition_ids = serializers.SerializerMethodField()

    @staticmethod
    def get_definition_ids(obj: QuestionnaireQuestion):
        return obj.related_definition_ordered.values_list("definition_id", flat=True)

    class Meta:
        model = QuestionnaireQuestion
        fields = [
            "criteria_id",
            "objectivity",
            "method",
            "definition_ids",
        ] + QUESTION_FIELDS
        read_only_fields = fields


class ProfilingQuestionSerializer(serializers.ModelSerializer):
    response_choices = ResponseChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = ProfilingQuestion
        fields = ["roles"] + QUESTION_FIELDS
        read_only_fields = fields


class CriteriaSerializer(serializers.ModelSerializer):
    question_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="questions"
    )

    class Meta:
        model = Criteria
        fields = [
            "id",
            "marker_id",
            "name",
            "concatenated_code",
            "question_ids",
            "thematic_tags",
        ] + REFERENTIAL_FIELDS
        read_only_fields = fields


class MarkerSerializer(serializers.ModelSerializer):
    criteria_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="criterias"
    )
    pillar_name = serializers.SerializerMethodField()

    @staticmethod
    def get_pillar_name(obj):
        return obj.pillar.name

    class Meta:
        model = Marker
        fields = [
            "id",
            "pillar_id",
            "pillar_name",
            "name",
            "concatenated_code",
            "criteria_ids",
        ] + REFERENTIAL_FIELDS
        read_only_fields = fields


class FullMarkerSerializer(MarkerSerializer):
    criterias = CriteriaSerializer(many=True, read_only=True)

    class Meta(MarkerSerializer.Meta):
        fields = MarkerSerializer.Meta.fields + ["criterias"]
        read_only_fields = fields


class PillarSerializer(serializers.ModelSerializer):
    marker_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="markers"
    )

    class Meta:
        model = Pillar
        fields = ["id", "name", "code", "description", "marker_ids"]
        read_only_fields = fields


class FullPillarSerializer(PillarSerializer):
    markers = FullMarkerSerializer(many=True, read_only=True)

    class Meta(PillarSerializer.Meta):
        fields = PillarSerializer.Meta.fields + ["markers"]
        read_only_fields = fields
