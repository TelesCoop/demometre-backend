import logging
import re

from datetime import date
from django.contrib.auth.models import User
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError, APIException

from open_democracy_back.models import Assessment
from open_democracy_back.models.assessment_models import (
    EPCI,
    InitiatorType,
    LocalityType,
    Municipality,
)
from open_democracy_back.models.representativity_models import (
    AssessmentRepresentativity,
    RepresentativityCriteria,
)
from open_democracy_back.serializers.assessment_serializers import AssessmentSerializer


# Get an instance of a logger
logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initialize_assessment(request, pk):
    initialize_data = request.data

    user = User.objects.get(pk=request.user.id)
    assessment = Assessment.objects.get(pk=pk)

    # Check that tje assessment is not already initialized
    if assessment.initialization_date:
        raise APIException(
            detail="The assessment is already initiated",
            code="assessment_already_initiated",
        )

    # Check if email user correspond to the initiator
    email_only_letters = re.sub(r"[^a-z]", "", user.email)
    initiator_name_only_letters = re.sub(
        r"[^a-z]",
        "",
        assessment.collectivity_name
        if initialize_data["initiator_type"] == InitiatorType.COLLECTIVITY
        else initialize_data["initiator_name"],
    )
    if initiator_name_only_letters not in email_only_letters:
        raise APIException(
            detail="The email is not corresponding to the assessment initiator",
            code="email_not_corresponding_assessment",
        )

    assessment.initiated_by_user = user
    assessment.initialization_date = date.today()
    if initialize_data["initiator_type"] in InitiatorType.values:
        assessment.initiator_type = initialize_data["initiator_type"]
    else:
        raise APIException(
            detail="The type of the assessment initiator is incorrect",
            code="incorrect_initiator_assessment",
        )
    assessment.initialized_to_the_name_of = initialize_data["initiator_name"]
    assessment.public_initiator = initialize_data["consent"]
    assessment.save()
    representativity_criterias = RepresentativityCriteria.objects.all()
    for representativity_criteria in representativity_criterias:
        representativity = AssessmentRepresentativity.objects.get_or_create(
            assessment=assessment, representativity_criteria=representativity_criteria
        )[0]
        # representativity_threshold as shape of [{"id": 1, "value":30}, {"id": 2, "value":20}]
        representativity.acceptability_threshold = next(
            threshold["value"]
            for threshold in initialize_data["representativity_thresholds"]
            if threshold["id"] == representativity_criteria.id
        )
        representativity.save()

    return Response(status=200, data=AssessmentSerializer(assessment).data)


class AssessmentsView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()

    def get_or_create(self, request):
        zip_code = request.GET.get("zip_code").replace(" ", "")
        locality_type = request.GET.get("locality_type")
        assessment = None
        if locality_type == LocalityType.MUNICIPALITY:

            municipality = Municipality.objects.filter(zip_codes__code=zip_code)
            if municipality.count() == 0:
                raise NotFound(
                    detail="The zip code does not correspond to any municipality",
                    code="no_zip_code_municipality",
                )
            if municipality.count() > 1:
                logger.warning(
                    f"There is several municipality corresponding to zip_code: {zip_code} (we are using the first occurence)"
                )
            assessment = Assessment.objects.get_or_create(
                type=locality_type, municipality=municipality.first()
            )
        elif locality_type == LocalityType.INTERCOMMUNALITY:
            epci = EPCI.objects.filter(
                related_municipalities_ordered__municipality__zip_codes__code=zip_code
            )
            if epci.count() == 0:
                raise NotFound(
                    detail="The zip code does not correspond to any epci",
                    code="no_zip_code_epci",
                )
            if epci.count() > 1:
                logger.warning(
                    f"There is several EPCI corresponding to zip_code: {zip_code} (we are using the first occurence)"
                )
            assessment = Assessment.objects.get_or_create(
                type=locality_type, epci=epci.first()
            )

        else:
            logger.error("locality_type received not correct")
            raise ValidationError(
                detail="The locality_type received is not correct",
                code="uncorrect_localitytype",
            )

        return Response(status=200, data=self.serializer_class(assessment[0]).data)


class AssessmentView(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()
