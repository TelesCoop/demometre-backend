from django.utils import timezone
from rest_framework import serializers

from open_democracy_back.fields.assessment_fields import AssessmentField
from open_democracy_back.fields.participation_fields import ParticipationField

from open_democracy_back.models.participation_models import Participation, Response
from open_democracy_back.models.questionnaire_and_profiling_models import (
    Role,
    Question,
    ResponseChoice,
)


class ParticipationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    assessment_id = AssessmentField(source="assessment")
    role_id = serializers.PrimaryKeyRelatedField(
        source="role", queryset=Role.objects.all()
    )

    def validate(self, data):
        if Participation.objects.filter(
            user_id=data["user"].id, assessment__initialization_date__lt=timezone.now()
        ).exists():
            raise serializers.ValidationError("You already have a participation.")
        return data

    class Meta:
        model = Participation
        fields = ["id", "user", "assessment_id", "role_id", "consent"]


class ResponseSerializer(serializers.ModelSerializer):
    participation_id = ParticipationField(source="participation")
    question_id = serializers.PrimaryKeyRelatedField(
        source="question", queryset=Question.objects.all()
    )
    unique_choice_response_id = serializers.PrimaryKeyRelatedField(
        source="unique_choice_response",
        queryset=ResponseChoice.objects.all(),
        required=False,
    )
    multiple_choice_response_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        source="multiple_choice_response",
        queryset=ResponseChoice.objects.all(),
        required=False,
    )

    class Meta:
        model = Response
        fields = [
            "id",
            "participation_id",
            "question_id",
            "unique_choice_response_id",
            "multiple_choice_response_ids",
            "boolean_response",
            "percentage_response",
        ]
        optional_fields = [
            "unique_choice_response_id",
            "multiple_choice_response_ids",
            "boolean_response",
            "percentage_response",
        ]
