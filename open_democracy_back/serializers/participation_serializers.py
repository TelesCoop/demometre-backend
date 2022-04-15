from django.utils import timezone
from rest_framework import serializers

from open_democracy_back.fields import FilteredPrimaryKeyRelatedField
from open_democracy_back.models.assessment_models import Assessment

from open_democracy_back.models.participation_models import Participation, Response
from open_democracy_back.models.questionnaire_and_profiling_models import (
    Role,
    Question,
    ResponseChoice,
)
from django.contrib.auth.models import User


class ParticipationSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all()
    )
    assessment_id = serializers.PrimaryKeyRelatedField(
        source="assessment", queryset=Assessment.objects.all()
    )
    role_id = serializers.PrimaryKeyRelatedField(
        source="role", queryset=Role.objects.all()
    )

    class Meta:
        model = Participation
        fields = ["id", "user_id", "assessment_id", "role_id", "consent"]


def get_participation_queryset(self):
    return Participation.objects.filter(
        user_id=self.context.get("request").user.id,
        assessment__initialization_date__lt=timezone.now(),
    )


class ResponseSerializer(serializers.ModelSerializer):
    participation_id = FilteredPrimaryKeyRelatedField(
        source="participation", get_queryset_fn=get_participation_queryset
    )
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

    def create(self, validated_data):
        response, created = Response.objects.update_or_create(
            question=validated_data.get("question"),
            participation=validated_data.get("participation"),
            defaults=validated_data,
        )
        return response
