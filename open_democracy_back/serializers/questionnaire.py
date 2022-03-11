from rest_framework import serializers

from open_democracy_back.models.questionnaire import (
    Criteria,
    Marker,
    Pillar,
    ProfilingQuestion,
    QuestionnaireQuestion,
    ResponseChoice,
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


class PillarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pillar
        fields = ["id", "name", "code", "description"]
        read_only_fields = fields


class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ["id", "pillar_id", "name", "concatenated_code"] + REFERENTIAL_FIELDS
        read_only_fields = fields


class CriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criteria
        fields = fields = [
            "id",
            "marker_id",
            "name",
            "concatenated_code",
            "thematic_tags",
        ] + REFERENTIAL_FIELDS
        read_only_fields = fields


class ResponseChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseChoice
        fields = ["id", "response_choice"]
        read_only_fields = fields


class QuestionnaireQuestionSerializer(serializers.ModelSerializer):
    response_choices = ResponseChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionnaireQuestion
        fields = ["criteria_id", "objectivity", "method"] + QUESTION_FIELDS
        read_only_fields = fields


class ProfilingQuestionSerializer(serializers.ModelSerializer):
    response_choices = ResponseChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = ProfilingQuestion
        fields = ["roles"] + QUESTION_FIELDS
        read_only_fields = fields
