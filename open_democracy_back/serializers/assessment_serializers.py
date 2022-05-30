from rest_framework import serializers
from open_democracy_back.exceptions import ErrorCode
from open_democracy_back.models.questionnaire_and_profiling_models import Question
from open_democracy_back.models.representativity_models import (
    RepresentativityCriteria,
)

from open_democracy_back.models.assessment_models import (
    EPCI,
    Assessment,
    AssessmentResponse,
    Municipality,
)
from open_democracy_back.serializers.participation_serializers import (
    OPTIONAL_RESPONSE_FIELDS,
    RESPONSE_FIELDS,
    AssessmentField,
    ResponseSerializer,
)
from open_democracy_back.serializers.representativity_serializers import (
    AssessmentRepresentativityCriteriaSerializer,
)
from open_democracy_back.serializers.user_serializers import UserSerializer


class MunicipalitySerializer(serializers.ModelSerializer):
    zip_codes = serializers.SerializerMethodField()

    @staticmethod
    def get_zip_codes(obj: Municipality):
        return obj.zip_codes.values_list("code", flat=True)

    class Meta:
        model = Municipality
        fields = [
            "id",
            "name",
            "population",
            "zip_codes",
        ]
        read_only_fields = fields


class EpciSerializer(serializers.ModelSerializer):
    zip_codes = serializers.SerializerMethodField()

    @staticmethod
    def get_zip_codes(obj: EPCI):
        zip_codes = []
        for municipality_order in obj.related_municipalities_ordered.all():
            zip_codes += [
                municipality_order.municipality.zip_codes.values_list("code", flat=True)
            ]
        return zip_codes

    class Meta:
        model = EPCI
        fields = [
            "id",
            "name",
            "population",
            "zip_codes",
        ]
        read_only_fields = fields


class AssessmentSerializer(serializers.ModelSerializer):
    epci = EpciSerializer(many=False, read_only=True)
    municipality = MunicipalitySerializer(many=False, read_only=True)
    participation_nb = serializers.SerializerMethodField()
    initiated_by_user = UserSerializer()
    representativities = serializers.SerializerMethodField()

    @staticmethod
    def get_representativities(obj: Assessment):
        representativities = []
        for representativity_criteria in RepresentativityCriteria.objects.all():
            representativities.append(
                AssessmentRepresentativityCriteriaSerializer(
                    representativity_criteria,
                    read_only=True,
                    context={"assessment_id": obj.id},
                ).data
            )
        return representativities

    @staticmethod
    def get_participation_nb(obj: Assessment):
        return obj.participations.count()

    class Meta:
        model = Assessment
        fields = [
            "id",
            "type",
            "initiated_by_user",
            "initiator_type",
            "initialized_to_the_name_of",
            "public_initiator",
            "initialization_date",
            "end_date",
            "municipality",
            "epci",
            "participation_nb",
            "representativities",
        ]
        read_only_fields = fields


class AssessmentResponseSerializer(ResponseSerializer):
    assessment_id = AssessmentField(source="assessment")

    def validate(self, data):
        assessment = data["assessment"]
        population = assessment.population
        if (
            not Question.objects.filter_by_population(population)
            .filter(id=data["question"].id)
            .exists()
        ):
            raise serializers.ValidationError(
                detail="You don't need to respond to this question.",
                code=ErrorCode.QUESTION_NOT_NEEDED.value,
            )
        question = data["question"]
        if question.objectivity == "subjective" or question.survey_type == "profiling":
            raise serializers.ValidationError(
                detail="A subjective response or profiling response must be link to the participation, not the assessment",
                code=ErrorCode.NEED_ASSESSMENT_RESPONSE.value,
            )
        return data

    class Meta:
        model = AssessmentResponse
        fields = RESPONSE_FIELDS + ["assessment_id"]
        optional_fields = OPTIONAL_RESPONSE_FIELDS
