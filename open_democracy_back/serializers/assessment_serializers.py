import datetime

from rest_framework import serializers

from my_auth.models import User
from open_democracy_back.exceptions import ErrorCode
from open_democracy_back.models import Participation, AssessmentDocument
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
    name = serializers.CharField(source="get_assessment_type_display")

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


def get_assessment_role(assessment: Assessment, user: User):
    if user.is_anonymous:
        return {"role": None}
    if assessment.initiated_by_user == user:
        return "initiator"
    if assessment.experts.filter(pk=user.pk).exists():
        return "expert"
    if Participation.objects.filter(assessment=assessment, user=user).exists():
        return "participant"
    return ""


def has_details_access(assessment_role):
    return assessment_role in ["expert", "initiator"]


class AssessmentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentDocument
        fields = [
            "assessment",
            "created",
            "category",
            "file",
            "id",
            "name",
        ]
        read_only_fields = ["created"]


class AssessmentSerializer(serializers.ModelSerializer):
    assessment_type = serializers.CharField(
        read_only=True, source="assessment_type.assessment_type"
    )
    documents = AssessmentDocumentSerializer(many=True)
    epci = EpciSerializer(many=False, read_only=True)
    experts = UserSerializer(many=True, read_only=True)
    initiated_by_user = UserSerializer(read_only=True)
    is_current = serializers.SerializerMethodField()
    municipality = MunicipalitySerializer(many=False, read_only=True)
    participation_count = serializers.SerializerMethodField()
    representativities = AssessmentRepresentativityCriteriaSerializer(
        many=True, read_only=True
    )
    details = serializers.SerializerMethodField()
    workshop_count = serializers.SerializerMethodField()

    def get_is_current(self, obj: Assessment):
        if not obj.end_date:
            return True
        return datetime.date.today() <= obj.end_date

    def get_details(self, obj: Assessment):
        if not (request := self.context.get("request", {})):
            return {"role": None}
        user = request.user
        role = get_assessment_role(obj, user)
        detail_access = has_details_access(role)
        to_return = {"role": role, "has_detail_access": detail_access}
        if not detail_access:
            return to_return
        return to_return

    @staticmethod
    def get_participation_count(obj: Assessment):
        return obj.participations.filter(user__is_unknown_user=False).count()

    def get_workshop_count(self, obj: Assessment):
        return obj.workshops.count()

    class Meta:
        model = Assessment
        fields = [
            "assessment_type",
            "conditions_of_sale_consent",
            "code",
            "collectivity_name",
            "calendar",
            "context",
            "created",
            "details",
            "documents",
            "end_date",
            "epci",
            "experts",
            "id",
            "initialization_date",
            "initialized_to_the_name_of",
            "initiated_by_user",
            "initiator_type",
            "initiator_usage_consent",
            "is_current",
            "is_initialization_questions_completed",
            "locality_type",
            "municipality",
            "objectives",
            "name",
            "participation_count",
            "published_results",
            "representativities",
            "stakeholders",
            "workshop_count",
        ]
        read_only_fields = [
            field
            for field in fields
            if field
            not in ["name", "context", "calendar", "objectives", "stakeholders"]
        ]


class AssessmentNoDetailSerializer(AssessmentSerializer):
    class Meta(AssessmentSerializer.Meta):
        fields = [
            field
            for field in AssessmentSerializer.Meta.fields
            if field not in ["context", "calendar", "objectives", "stakeholders"]
        ]


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
