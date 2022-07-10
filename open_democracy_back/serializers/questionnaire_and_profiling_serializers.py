from rest_framework import serializers

from open_democracy_back.models.questionnaire_and_profiling_models import (
    Criteria,
    Marker,
    Pillar,
    ProfilingQuestion,
    QuestionRule,
    QuestionnaireQuestion,
    ResponseChoice,
    Definition,
    Role,
    Category,
)

QUESTION_FIELDS = [
    "id",
    "concatenated_code",
    "name",
    "question_statement",
    "description",
    "mandatory",
    "type",
    "response_choices",
    "max_multiple_choices",
    "categories",
    "rules_intersection_operator",
    "rules",
    "survey_type",
    "role_ids",
    "population_lower_bound",
    "population_upper_bound",
]
STRENGTHS_AND_WEAKNESSES_FIELDS = [
    "weakness_1",
    "weakness_2",
    "strength_3",
    "strength_4",
]
SCORE_FIELDS = [
    "score_1",
    "score_2",
    "score_3",
    "score_4",
]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]
        read_only_fields = fields


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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category"]
        read_only_fields = fields


class QuestionRuleSerializer(serializers.ModelSerializer):
    conditional_question_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source="conditional_question"
    )
    response_choice_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="response_choices"
    )

    class Meta:
        model = QuestionRule
        fields = [
            "id",
            "conditional_question_id",
            "response_choice_ids",
            "numerical_operator",
            "numerical_value",
            "boolean_response",
            "type",
        ]
        read_only_fields = fields


class QuestionSerializer(serializers.ModelSerializer):
    response_choices = ResponseChoiceSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    rules = QuestionRuleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        read_only=True, source="roles", many=True
    )

    class Meta:
        abstract = True


class QuestionnaireQuestionSerializer(QuestionSerializer):
    profile_ids = serializers.PrimaryKeyRelatedField(
        read_only=True, source="profiles", many=True
    )
    pillar_id = serializers.SerializerMethodField()
    pillar_name = serializers.SerializerMethodField()

    @staticmethod
    def get_pillar_name(obj):
        return obj.criteria.marker.pillar.name

    @staticmethod
    def get_pillar_id(obj):
        return obj.criteria.marker.pillar_id

    class Meta:
        model = QuestionnaireQuestion
        fields = [
            "criteria_id",
            "pillar_name",
            "pillar_id",
            "objectivity",
            "method",
            "profile_ids",
        ] + QUESTION_FIELDS
        read_only_fields = fields


class ProfilingQuestionSerializer(QuestionSerializer):
    class Meta:
        model = ProfilingQuestion
        fields = QUESTION_FIELDS
        read_only_fields = fields


class CriteriaSerializer(serializers.ModelSerializer):
    question_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="questions"
    )
    definition_ids = serializers.SerializerMethodField()

    @staticmethod
    def get_definition_ids(obj: Criteria):
        return obj.related_definition_ordered.values_list("definition_id", flat=True)

    class Meta:
        model = Criteria
        fields = [
            "id",
            "marker_id",
            "name",
            "concatenated_code",
            "question_ids",
            "thematic_tags",
            "definition_ids",
            "explanatory",
            "description",
        ] + STRENGTHS_AND_WEAKNESSES_FIELDS
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
        fields = (
            [
                "id",
                "pillar_id",
                "pillar_name",
                "name",
                "concatenated_code",
                "criteria_ids",
                "description",
            ]
            + SCORE_FIELDS
            + STRENGTHS_AND_WEAKNESSES_FIELDS
        )
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
