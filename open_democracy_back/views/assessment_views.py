import logging
from datetime import date
from typing import Dict
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response as RestResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from my_auth.models import User

from open_democracy_back.exceptions import ErrorCode, ValidationFieldError
from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin

from open_democracy_back.models import (
    Assessment,
)
from open_democracy_back.models.assessment_models import (
    EPCI,
    AssessmentResponse,
    InitiatorType,
    LocalityType,
    Municipality,
)
from open_democracy_back.models.representativity_models import (
    AssessmentRepresentativity,
    RepresentativityCriteria,
)
from open_democracy_back.permissions import IsAssessmentAdminOrReadOnly
from open_democracy_back.scoring import (
    get_scores_by_assessment_pk,
)
from open_democracy_back.serializers.assessment_serializers import (
    AssessmentResponseSerializer,
    AssessmentSerializer,
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initialize_assessment(request, pk):
    initialize_data = request.data

    user = User.objects.get(pk=request.user.id)
    assessment = Assessment.objects.get(pk=pk)

    # Check that the assessment is not already initialized
    if assessment.initialization_date:
        raise APIException(
            detail="The assessment is already initiated",
            code=ErrorCode.ASSESSMENT_ALREADY_INITIATED.value,
        )

    # # Check if email user correspond to the initiator
    # email_only_letters = re.sub(r"[^a-z]", "", user.email)
    # initiator_name_only_letters = re.sub(
    #     r"[^a-z]",
    #     "",
    #     assessment.collectivity_name
    #     if initialize_data["initiator_type"] == InitiatorType.COLLECTIVITY
    #     else initialize_data["initiator_name"],
    # )
    # if initiator_name_only_letters not in email_only_letters:
    #     raise ValidationFieldError(
    #         "initiator_name",
    #         detail="The email is not corresponding to the assessment initiator",
    #         code=ErrorCode.EMAIL_NOT_CORRESPONDING_ASSESSMENT.value,
    #     )

    assessment.initiated_by_user = user
    assessment.initialization_date = date.today()
    if initialize_data["initiator_type"] in InitiatorType.values:
        assessment.initiator_type = initialize_data["initiator_type"]
    else:
        raise ValidationFieldError(
            "initiator_type",
            detail="The type of the assessment initiator is incorrect",
            code=ErrorCode.INCORRECT_INITIATOR_ASSESSMENT.value,
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

    return RestResponse(status=200, data=AssessmentSerializer(assessment).data)


class AssessmentsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()

    def get_or_create(self, request):
        zip_code = request.GET.get("zip_code").replace(" ", "")
        locality_type = request.GET.get("locality_type")
        assessment = None
        if locality_type == LocalityType.MUNICIPALITY:

            municipality = Municipality.objects.filter(zip_codes__code=zip_code)
            if municipality.count() == 0:
                raise ValidationFieldError(
                    "zip_code",
                    detail="The zip code does not correspond to any municipality",
                    code=ErrorCode.NO_ZIP_CODE_MUNICIPALITY.value,
                )
            if municipality.count() > 1:
                logger.warning(
                    f"There is several municipality corresponding to zip_code: {zip_code} (we are using the first occurence)"
                )
            assessment = Assessment.objects.get_or_create(
                locality_type=locality_type, municipality=municipality.first()
            )
        elif locality_type == LocalityType.INTERCOMMUNALITY:
            epci = EPCI.objects.filter(
                related_municipalities_ordered__municipality__zip_codes__code=zip_code
            )
            if epci.count() == 0:
                raise ValidationFieldError(
                    "zip_code",
                    detail="The zip code does not correspond to any epci",
                    code=ErrorCode.NO_ZIP_CODE_EPCI.value,
                )
            if epci.count() > 1:
                logger.warning(
                    f"There is several EPCI corresponding to zip_code: {zip_code} (we are using the first occurence)"
                )
            assessment = Assessment.objects.get_or_create(
                locality_type=locality_type, epci=epci.first()
            )

        else:
            logger.error("locality_type received not correct")
            raise ValidationFieldError(
                "locality_type",
                detail="The locality type received is not correct",
                code=ErrorCode.UNCORRECT_LOCALITY_TYPE.value,
            )

        return RestResponse(status=200, data=self.serializer_class(assessment[0]).data)


class AnimatorAssessmentsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        return Assessment.objects.filter(
            initialization_date__lte=timezone.now(),
            expert=self.request.user,
            royalty_payed=True,
        ).exclude(end_date__lt=timezone.now())


class AssessmentView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()


class AssessmentResponseView(
    mixins.ListModelMixin, UpdateOrCreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAssessmentAdminOrReadOnly]
    serializer_class = AssessmentResponseSerializer

    def get_queryset(self):
        return AssessmentResponse.objects.filter(
            assessment=self.request.query_params.get("assessment_id")
        )

    def get_or_update_object(self, request):
        return AssessmentResponse.objects.get(
            assessment_id=request.data.get("assessment_id"),
            question_id=request.data.get("question_id"),
        )


class CompletedQuestionsInitializationView(APIView):
    permission_classes = [IsAssessmentAdminOrReadOnly]

    def patch(self, _, assessment_pk):
        assessment = Assessment.objects.get(id=assessment_pk)
        assessment.is_initialization_questions_completed = True
        assessment.save()

        serializer = AssessmentSerializer(assessment)
        return RestResponse(serializer.data, status=status.HTTP_200_OK)


class QuestionnaireScoreView(APIView):
    # Cache page everyday
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, assessment_pk):
        scores: Dict[str, Dict[str, float]] = get_scores_by_assessment_pk(assessment_pk)
        return RestResponse(scores, status=status.HTTP_200_OK)
