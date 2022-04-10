from rest_framework import serializers
from open_democracy_back.models.assessment_models import Assessment

from open_democracy_back.models.participation_models import Participation, Response
from open_democracy_back.models.questionnaire_and_profiling_models import (
    Role,
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


class ResponseSerializer(serializers.ModelSerializer):
    participation_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source="participation"
    )
    question_id = serializers.PrimaryKeyRelatedField(read_only=True, source="question")
    unique_choice_response_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source="unique_choice_response"
    )
    multiple_choice_response_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="unique_choice_response"
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
