from rest_framework import serializers

from open_democracy_back.models.representativity_models import (
    AssessmentRepresentativity,
    RepresentativityCriteria,
)


class AssessmentRepresentativityCriteriaSerializer(serializers.ModelSerializer):
    """
    Count by response choice for all representativity criteria link to a specific assessment
    Need "assessment_id" in context arg
    """

    assessment_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source="assessment"
    )
    representativity_criteria_name = serializers.CharField(
        read_only=True, source="representativity_criteria.name"
    )

    class Meta:
        model = AssessmentRepresentativity
        fields = [
            "id",
            "assessment_id",
            "representativity_criteria_name",
            "count_by_response_choice",
            "acceptability_threshold_considered",
            "respected",
        ]
        read_only_fields = fields


class RepresentativityCriteriaSerializer(serializers.ModelSerializer):
    profiling_question_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source="profiling_question"
    )
    response_choice_statements = serializers.SerializerMethodField()

    def get_response_choice_statements(self, obj: RepresentativityCriteria):
        return obj.profiling_question.response_choices.all().values(
            "id", "response_choice"
        )

    class Meta:
        model = RepresentativityCriteria
        fields = [
            "id",
            "name",
            "profiling_question_id",
            "min_rate",
            "response_choice_statements",
        ]
        read_only_fields = fields
