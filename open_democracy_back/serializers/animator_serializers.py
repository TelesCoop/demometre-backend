from rest_framework import serializers
from open_democracy_back.models.animator_models import Participant, Workshop
from open_democracy_back.models.assessment_models import Assessment
from open_democracy_back.models.participation_models import (
    Participation,
    ParticipationResponse,
)
from open_democracy_back.models.questionnaire_and_profiling_models import Role
from open_democracy_back.serializers.assessment_serializers import (
    AssessmentResponseSerializer,
)
from open_democracy_back.serializers.participation_serializers import (
    OPTIONAL_RESPONSE_FIELDS,
    RESPONSE_FIELDS,
    ResponseSerializer,
)


class WorkshopParticipationResponseSerializer(ResponseSerializer):
    participation_id = serializers.PrimaryKeyRelatedField(
        source="participation", queryset=Participation.objects.all()
    )
    # TODO : make a validation function as ParticipationResponseSerializer

    class Meta:
        model = ParticipationResponse
        fields = RESPONSE_FIELDS + ["participation_id"]
        optional_fields = OPTIONAL_RESPONSE_FIELDS


class WorkshopParticipationWithProfilingResponsesSerializer(
    serializers.ModelSerializer
):
    participant_id = serializers.PrimaryKeyRelatedField(
        source="participant", queryset=Participant.objects.all(), required=False
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

    participant_email = serializers.SerializerMethodField()
    participant_name = serializers.SerializerMethodField()
    responses = WorkshopParticipationResponseSerializer(
        many=True, required=False, read_only=True
    )

    @staticmethod
    def get_participant_email(obj: Participation):
        return obj.participant.email

    @staticmethod
    def get_participant_name(obj: Participation):
        return obj.participant.name

    class Meta:
        model = Participation
        fields = [
            "id",
            "participant_id",
            "participant_email",
            "participant_name",
            "assessment_id",
            "workshop_id",
            "role_id",
            "responses",
        ]
        optional_fields = ["participant_id"]


class WorkshopSerializer(serializers.ModelSerializer):
    animator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    assessment_id = serializers.PrimaryKeyRelatedField(
        source="assessment", queryset=Assessment.objects.all()
    )
    participation_ids = serializers.PrimaryKeyRelatedField(
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
            "closed",
            "participation_ids",
        ]


class FullWorkshopSerializer(WorkshopSerializer):
    participations = WorkshopParticipationWithProfilingResponsesSerializer(
        many=True, read_only=True
    )
    assessment_responses = serializers.SerializerMethodField()

    @staticmethod
    def get_assessment_responses(obj: Workshop):
        responses = []
        for assessment_response in obj.assessment.responses.all():
            responses.append(
                AssessmentResponseSerializer(
                    assessment_response,
                    read_only=True,
                ).data
            )
        return responses

    class Meta:
        model = Workshop
        fields = WorkshopSerializer.Meta.fields + [
            "participations",
            "assessment_responses",
        ]