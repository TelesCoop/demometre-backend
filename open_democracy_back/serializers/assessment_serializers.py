from rest_framework import serializers
from open_democracy_back.models.representativity_models import (
    RepresentativityCriteria,
)

from open_democracy_back.models.assessment_models import EPCI, Assessment, Municipality
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
    initiated_by = UserSerializer()
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
            "initiated_by",
            "is_initiated_by_locality",
            "carried_by",
            "is_carried_by_locality",
            "initialization_date",
            "end_date",
            "municipality",
            "epci",
            "participation_nb",
            "representativities",
        ]
        read_only_fields = fields
