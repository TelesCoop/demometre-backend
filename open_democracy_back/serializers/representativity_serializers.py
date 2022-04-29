from django.db.models import Count, F
from rest_framework import serializers

from open_democracy_back.models.representativity_models import (
    RepresentativityCriteria,
)


class AssessmentRepresentativityCriteriaSerializer(serializers.ModelSerializer):
    """
    Count by response choice for all representativity criteria link to a specific assessment
    Need "assessment_id" in context arg
    """

    profiling_question_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source="profiling_question"
    )
    count_by_response_choice = serializers.SerializerMethodField()

    def get_count_by_response_choice(self, obj: RepresentativityCriteria):
        # annotate() : rename field
        # values() : specifies which columns are going to be used to "group by"
        # annotate() : specifies an operation over the grouped values
        return (
            obj.profiling_question.responses.filter(
                participation__assessment_id=self.context.get("assessment_id")
            )
            .annotate(
                response_choice_name=F("unique_choice_response__response_choice"),
                response_choice_id=F("unique_choice_response"),
            )
            .values("response_choice_id", "response_choice_name")
            .annotate(total=Count("response_choice_id"))
        )

    class Meta:
        model = RepresentativityCriteria
        fields = [
            "id",
            "name",
            "profiling_question_id",
            "min_rate",
            "count_by_response_choice",
        ]
        read_only_fields = fields


class RepresentativityCriteriaSerializer(serializers.ModelSerializer):
    profiling_question_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source="profiling_question"
    )
    response_choice_statements = serializers.SerializerMethodField()

    def get_response_choice_statements(self, obj: RepresentativityCriteria):
        return obj.profiling_question.response_choices.all().values_list(
            "response_choice", flat=True
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
