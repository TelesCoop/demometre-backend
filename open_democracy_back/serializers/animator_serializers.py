from my_auth.models import User
from rest_framework import serializers
from open_democracy_back.models.animator_models import Workshop
from open_democracy_back.models.assessment_models import Assessment
from open_democracy_back.models.participation_models import (
    Participation,
    ParticipationResponse,
)
from open_democracy_back.models.questionnaire_and_profiling_models import Role
from open_democracy_back.serializers.participation_serializers import (
    OPTIONAL_RESPONSE_FIELDS,
    RESPONSE_FIELDS,
    ResponseSerializer,
)


class ParticipantResponseSerializer(ResponseSerializer):
    participation_id = serializers.PrimaryKeyRelatedField(
        source="participation", queryset=Participation.objects.all()
    )
    # TODO : make a validation function as ParticipationResponseSerializer

    class Meta:
        model = ParticipationResponse
        fields = RESPONSE_FIELDS + ["participation_id"]
        optional_fields = OPTIONAL_RESPONSE_FIELDS


class ParticipantWithProfilingResponsesSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), required=False
    )
    assessment_id = serializers.PrimaryKeyRelatedField(
        source="assessment", queryset=Assessment.objects.all()
    )
    role_id = serializers.PrimaryKeyRelatedField(
        source="role", queryset=Role.objects.all()
    )
    workshop_id = serializers.PrimaryKeyRelatedField(
        source="workshop", queryset=Workshop.objects.all()
    )

    user_email = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    responses = ParticipantResponseSerializer(many=True, required=False, read_only=True)

    @staticmethod
    def get_user_email(obj: Participation):
        return obj.user.email

    @staticmethod
    def get_user_username(obj: Participation):
        return obj.user.username

    class Meta:
        model = Participation
        fields = [
            "id",
            "user_id",
            "user_email",
            "user_username",
            "assessment_id",
            "workshop_id",
            "role_id",
            "responses",
        ]
        optional_fields = ["user_id"]


class WorkshopSerializer(serializers.ModelSerializer):
    animator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    assessment_id = serializers.PrimaryKeyRelatedField(
        source="assessment", queryset=Assessment.objects.all()
    )
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="participations"
    )

    class Meta:
        model = Workshop
        fields = [
            "id",
            "name",
            "animator",
            "assessment_id",
            "date",
            "participant_ids",
        ]


class FullWorkshopSerializer(WorkshopSerializer):
    participants = ParticipantWithProfilingResponsesSerializer(
        source="participations", many=True, read_only=True
    )

    class Meta:
        model = Workshop
        fields = WorkshopSerializer.Meta.fields + ["participants"]
