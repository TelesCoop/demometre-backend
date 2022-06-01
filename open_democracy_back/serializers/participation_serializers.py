from django.utils import timezone
from rest_framework import serializers
from my_auth.serializers import CurrentUserOrAnonymousField
from my_auth.utils import get_authenticated_or_anonymous_user_from_request
from open_democracy_back.exceptions import ErrorCode

from open_democracy_back.models import Assessment

from open_democracy_back.models.participation_models import (
    Participation,
    ParticipationResponse,
    ParticipationPillarCompleted,
)
from open_democracy_back.models.questionnaire_and_profiling_models import (
    Role,
    Question,
    ResponseChoice,
)

RESPONSE_FIELDS = [
    "id",
    "question_id",
    "has_passed",
    "unique_choice_response_id",
    "multiple_choice_response_ids",
    "boolean_response",
    "percentage_response",
]
OPTIONAL_RESPONSE_FIELDS = [
    "unique_choice_response_id",
    "multiple_choice_response_ids",
    "boolean_response",
    "percentage_response",
]


class AssessmentField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return Assessment.objects.filter(initialization_date__lte=timezone.now())


class ParticipationField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user_id = get_authenticated_or_anonymous_user_from_request(
            self.context.get("request")
        ).id
        return Participation.objects.filter(
            user_id=user_id,
            assessment__initialization_date__lte=timezone.now(),
        )


class ParticipationPillarCompletedSerializer(serializers.ModelSerializer):
    participation_id = serializers.PrimaryKeyRelatedField(
        source="participation", read_only=True
    )
    pillar_id = serializers.PrimaryKeyRelatedField(source="pillar", read_only=True)

    class Meta:
        model = ParticipationPillarCompleted
        fields = ["participation_id", "pillar_id", "completed"]


class ParticipationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserOrAnonymousField())
    assessment_id = AssessmentField(source="assessment")
    role_id = serializers.PrimaryKeyRelatedField(
        source="role", queryset=Role.objects.all()
    )
    is_pillar_questions_completed = ParticipationPillarCompletedSerializer(
        source="participationpillarcompleted_set", many=True, read_only=True
    )
    profile_ids = serializers.PrimaryKeyRelatedField(
        read_only=True, source="profiles", many=True
    )

    def validate(self, data):
        if Participation.objects.filter(
            user_id=data["user"].id, assessment__initialization_date__lt=timezone.now()
        ).exists():
            raise serializers.ValidationError(
                detail="The participation already exists",
                code=ErrorCode.PARTICIPATION_ALREADY_EXISTS.value,
            )
        return data

    class Meta:
        model = Participation
        fields = [
            "id",
            "user",
            "assessment_id",
            "role_id",
            "consent",
            "is_profiling_questions_completed",
            "is_pillar_questions_completed",
            "profile_ids",
        ]
        read_only_fields = ["is_profiling_questions_completed"]


class ResponseSerializer(serializers.ModelSerializer):
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
        asbtract = True


class ParticipationResponseSerializer(ResponseSerializer):
    participation_id = ParticipationField(source="participation")

    def validate(self, data):
        participation = data["participation"]
        population = participation.assessment.population
        if (
            not Question.objects.filter_by_role(participation.role)
            .filter_by_population(population)
            .filter(id=data["question"].id)
            .exists()
        ):
            raise serializers.ValidationError(
                detail="You don't need to respond to this question.",
                code=ErrorCode.QUESTION_NOT_NEEDED.value,
            )
        question = data["question"]
        if (
            question.objectivity == "objective"
            and question.survey_type == "questionnaire"
        ):
            raise serializers.ValidationError(
                detail="An objective response must be link to the assessment, not the participation",
                code=ErrorCode.NEED_PARTICIPATION_RESPONSE.value,
            )
        return data

    class Meta:
        model = ParticipationResponse
        fields = RESPONSE_FIELDS + ["participation_id"]
        optional_fields = OPTIONAL_RESPONSE_FIELDS
