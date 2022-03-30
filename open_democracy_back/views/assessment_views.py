import logging
from rest_framework import mixins, viewsets
from rest_framework.response import Response

from open_democracy_back.models import Assessment
from open_democracy_back.models.assessment_models import (
    EPCI,
    LocalityType,
    Municipality,
)
from open_democracy_back.serializers.assessment_serializers import AssessmentSerializer


# Get an instance of a logger
logger = logging.getLogger(__name__)


class AssessmentsView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()

    def get_or_create(self, request):
        zip_code = request.GET.get("zip_code")
        locality_type = request.GET.get("locality_type")
        assessment = None
        if locality_type == LocalityType.MUNICIPALITY:

            municipality = Municipality.objects.filter(zip_codes__code=zip_code)
            if municipality.count() == 0:
                return Response(
                    status=400, data="Aucune commune ne correspond à ce code postal"
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
                return Response(
                    status=400,
                    data="Aucune intercommunalité ne correspond à ce code postal",
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
            return Response(status=400)

        return Response(status=200, data=self.serializer_class(assessment[0]).data)


class AssessmentView(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()
