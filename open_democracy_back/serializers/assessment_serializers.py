from rest_framework import serializers

from open_democracy_back.exceptions import ErrorCode
from open_democracy_back.models import Participation
from open_democracy_back.models.questionnaire_and_profiling_models import Question

from open_democracy_back.models.assessment_models import (
    EPCI,
    Assessment,
    AssessmentResponse,
    AssessmentType,
    Municipality,
)
from open_democracy_back.serializers.participation_serializers import (
    OPTIONAL_RESPONSE_FIELDS,
    RESPONSE_FIELDS,
    ResponseSerializer,
)
from open_democracy_back.serializers.representativity_serializers import (
    AssessmentRepresentativityCriteriaSerializer,
)
from open_democracy_back.serializers.user_serializers import UserSerializer
from open_democracy_back.utils import LocalityType


class MunicipalitySerializer(serializers.ModelSerializer):
    zip_codes = serializers.SerializerMethodField()
    locality_type = serializers.SerializerMethodField()

    @staticmethod
    def get_zip_codes(obj: Municipality):
        return obj.zip_codes.values_list("code", flat=True)

    @staticmethod
    def get_locality_type(_):
        return LocalityType.MUNICIPALITY

    class Meta:
        model = Municipality
        fields = [
            "id",
            "name",
            "population",
            "zip_codes",
            "locality_type",
        ]
        read_only_fields = fields


class EpciSerializer(serializers.ModelSerializer):
    zip_codes = serializers.SerializerMethodField()
    locality_type = serializers.SerializerMethodField()

    @staticmethod
    def get_zip_codes(obj: EPCI):
        zip_codes = []
        for municipality_order in obj.related_municipalities_ordered.all():
            zip_codes += [
                municipality_order.municipality.zip_codes.values_list("code", flat=True)
            ]
        return zip_codes

    @staticmethod
    def get_locality_type(_):
        return LocalityType.INTERCOMMUNALITY

    class Meta:
        model = EPCI
        fields = [
            "id",
            "name",
            "population",
            "zip_codes",
            "locality_type",
        ]
        read_only_fields = fields


class AssessmentTypeSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    @staticmethod
    def get_pdf_url(obj: AssessmentType):
        if obj.pdf:
            return obj.pdf.file.url
        return None

    class Meta:
        model = AssessmentType
        fields = [
            "id",
            "name",
            "assessment_type",
            "for_who",
            "what",
            "for_what",
            "results",
            "price",
            "pdf_url",
        ]
        read_only_fields = fields


class AssessmentSerializer(serializers.ModelSerializer):
    epci = EpciSerializer(many=False, read_only=True)
    municipality = MunicipalitySerializer(many=False, read_only=True)
    participation_nb = serializers.SerializerMethodField()
    initiated_by_user = UserSerializer(read_only=True)
    representativities = AssessmentRepresentativityCriteriaSerializer(
        many=True, read_only=True
    )
    experts = UserSerializer(many=True, read_only=True)
    assessment_type = serializers.CharField(
        read_only=True, source="assessment_type.assessment_type"
    )

    @staticmethod
    def get_participation_nb(obj: Assessment):
        return obj.participations.count()

    class Meta:
        model = Assessment
        fields = [
            "id",
            "assessment_type",
            "conditions_of_sale_consent",
            "locality_type",
            "initiated_by_user",
            "initiator_type",
            "initiator_usage_consent",
            "initialized_to_the_name_of",
            "initialization_date",
            "is_initialization_questions_completed",
            "end_date",
            "municipality",
            "epci",
            "participation_nb",
            "representativities",
            "published_results",
            "experts",
        ]
        read_only_fields = fields


class AssessmentResponseSerializer(ResponseSerializer):
    assessment_id = serializers.PrimaryKeyRelatedField(
        source="assessment", queryset=Assessment.objects.all()
    )
    answered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, data):
        assessment = data["assessment"]
        population = assessment.population
        user = self.context["request"].user

        question = data["question"]

        is_initiator = assessment.initiated_by_user.id == user.id
        is_expert = assessment.experts.filter(id=user.id).exists()

        # Filter role and profile if the user is not an initiator or expert
        if not (is_initiator or is_expert):
            participation = Participation.objects.get(
                assessment_id=assessment.pk,
                id=self.context["request"].data["participation_id"],
                user=user,
            )
            questions = Question.objects.filter_by_role(
                participation.role
            ).filter_by_profiles(participation.profiles.all())
        else:
            questions = Question.objects

        if (
            not questions.filter_by_population(population)
            .filter(id=data["question"].id)
            .exists()
        ):
            raise serializers.ValidationError(
                detail="You don't need to respond to this question.",
                code=ErrorCode.QUESTION_NOT_NEEDED.value,
            )
        if question.objectivity == "subjective" or question.survey_type == "profiling":
            raise serializers.ValidationError(
                detail="A subjective response or profiling response must be link to the participation, not the assessment",
                code=ErrorCode.NEED_ASSESSMENT_RESPONSE.value,
            )
        return data

    class Meta:
        model = AssessmentResponse
        fields = RESPONSE_FIELDS + ["assessment_id", "answered_by"]
        optional_fields = OPTIONAL_RESPONSE_FIELDS
