import logging
from datetime import date
from typing import Dict

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response as RestResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from my_auth.models import User
from my_auth.serializers import UserSerializer

from open_democracy_back.chart_data import CHART_DATA_FN_BY_QUESTION_TYPE
from open_democracy_back.exceptions import ErrorCode, ValidationFieldError
from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin

from open_democracy_back.models import (
    Assessment,
    Participation,
    Question,
)
from open_democracy_back.models.assessment_models import (
    EPCI,
    AssessmentResponse,
    AssessmentType,
    InitiatorType,
    LocalityType,
    Municipality,
)
from open_democracy_back.models.representativity_models import (
    AssessmentRepresentativity,
    RepresentativityCriteria,
)
from open_democracy_back.scoring import (
    get_scores_by_assessment_pk,
)
from open_democracy_back.serializers.assessment_serializers import (
    AssessmentResponseSerializer,
    AssessmentSerializer,
    EpciSerializer,
    MunicipalitySerializer,
)
from open_democracy_back.utils import ManagedAssessmentType

logger = logging.getLogger(__name__)


def consent_condition_of_sales(assessment, conditions_of_sale_consent):
    if conditions_of_sale_consent is True:
        assessment.conditions_of_sale_consent = True
    else:
        raise ValidationFieldError(
            "conditions_of_sale_consent",
            detail="To initialize an expert assessment, the conditions of sale must be consented",
            code=ErrorCode.CGV_MUST_BE_CONSENTED.value,
        )


# TODO : update existing assessment
# @api_view(["PATCH"])
# @permission_classes([IsAuthenticated])
# def update_assessment(request, pk):


class AssessmentsView(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()

    @action(detail=False, methods=["GET"])
    def mine(self, request):
        assessments = Assessment.objects.filter(
            participations__in=Participation.objects.filter_available(
                self.request.user, timezone.now()
            ),
        )
        return RestResponse(
            status=200,
            data=self.serializer_class(
                assessments, many=True, context=self.get_serializer_context()
            ).data,
        )

    @action(detail=False, methods=["GET"], url_path="by-animator")
    def by_animator(self, request):
        assessments = Assessment.objects.filter(
            initialization_date__lte=timezone.now(),
            experts__in=[self.request.user],
            royalty_payed=True,
        ).exclude(end_date__lt=timezone.now())
        return RestResponse(
            status=200,
            data=self.serializer_class(
                assessments, context=self.get_serializer_context(), many=True
            ).data,
        )

    @action(detail=False, methods=["GET"])
    def published(self, request):
        assessments = Assessment.objects.filter(initialization_date__lte=timezone.now())
        assessments = [
            assessment for assessment in assessments if assessment.published_results
        ]
        return RestResponse(
            status=200,
            data=self.serializer_class(
                assessments, context=self.get_serializer_context(), many=True
            ).data,
        )

    @action(detail=False, methods=["GET"])
    def current(self, request):
        # TODO change request
        current_assessment = Assessment.objects.filter(
            participations__in=Participation.objects(self.request.user, timezone.now()),
        ).first()
        serializer = AssessmentSerializer(
            current_assessment, context=self.get_serializer_context()
        )
        return RestResponse(serializer.data)

    @permission_classes([IsAuthenticated])
    @action(detail=True, methods=["POST"], url_path="initialization")
    def initialize_assessment(self, request, pk):
        with transaction.atomic():
            initialize_data = request.data
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

            assessment.initiated_by_user = request.user
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
            assessment_type = AssessmentType.objects.get(
                assessment_type=initialize_data["assessment_type"]
            )
            assessment.assessment_type = assessment_type
            if initialize_data["assessment_type"] == ManagedAssessmentType.WITH_EXPERT:
                consent_condition_of_sales(
                    assessment, request.data.get("conditions_of_sale_consent")
                )
            if request.data.get("initiator_usage_consent") is True:
                assessment.initiator_usage_consent = True
            else:
                raise ValidationFieldError(
                    "initiator_usage_consent",
                    detail="To initialize an assessment, the initator must consent the conditions of use",
                    code=ErrorCode.CGU_MUST_BE_CONSENTED.value,
                )
            assessment.initiator_usage_consent = request.data.get(
                "initiator_usage_consent"
            )
            assessment.save()
            representativity_criterias = RepresentativityCriteria.objects.all()
            for representativity_criteria in representativity_criterias:
                representativity = AssessmentRepresentativity.objects.get_or_create(
                    assessment=assessment,
                    representativity_criteria=representativity_criteria,
                )[0]
                # representativity_threshold as shape of [{"id": 1, "value":30}, {"id": 2, "value":20}]
                representativity.acceptability_threshold = next(
                    threshold["value"]
                    for threshold in initialize_data["representativity_thresholds"]
                    if threshold["id"] == representativity_criteria.id
                )
                representativity.save()

            return RestResponse(
                status=200,
                data=AssessmentSerializer(
                    assessment, context=self.get_serializer_context()
                ).data,
            )

    def get_or_create(self, request):
        if request.user.is_anonymous:
            user_id = None
        else:
            user_id = request.user.id
        locality_id = request.GET.get("locality_id")
        locality_type = request.GET.get("locality_type")
        assessment = None
        assessments_usable = Assessment.objects.all().exclude(
            Q(assessment_type__assessment_type=ManagedAssessmentType.QUICK)
            & ~Q(initiated_by_user_id=user_id)
        )
        if locality_type == LocalityType.MUNICIPALITY:
            municipality = Municipality.objects.get(id=locality_id)
            assessment, _ = assessments_usable.get_or_create(
                locality_type=locality_type, municipality=municipality
            )
        elif locality_type == LocalityType.INTERCOMMUNALITY:
            epci = EPCI.objects.get(id=locality_id)
            assessment, _ = assessments_usable.get_or_create(
                locality_type=locality_type, epci=epci
            )

        else:
            logger.error("locality_type received not correct")
            raise ValidationFieldError(
                "locality_type",
                detail="The locality type received is not correct",
                code=ErrorCode.UNCORRECT_LOCALITY_TYPE.value,
            )

        return RestResponse(status=200, data=self.serializer_class(assessment).data)


class ZipCodeLocalitiesView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class_municipality = MunicipalitySerializer
    serializer_class_epci = EpciSerializer

    def list(self, request, zip_code):
        municipalities = self.serializer_class_municipality(
            Municipality.objects.filter(zip_codes__code=zip_code).distinct(), many=True
        )
        epcis = self.serializer_class_epci(
            EPCI.objects.filter(
                related_municipalities_ordered__municipality__zip_codes__code=zip_code
            ).distinct(),
            many=True,
        )
        return Response(
            {
                LocalityType.MUNICIPALITY: municipalities.data,
                LocalityType.INTERCOMMUNALITY: epcis.data,
            }
        )


class AssessmentResponseView(
    mixins.ListModelMixin, UpdateOrCreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentResponseSerializer

    def get_queryset(self):
        return AssessmentResponse.objects.filter(
            assessment__participations__in=Participation.objects.filter_available(
                self.request.user.id, timezone.now()
            ),
        )

    def get_or_update_object(self, request):
        return AssessmentResponse.objects.get(
            assessment_id=request.data.get("assessment_id"),
            question_id=request.data.get("question_id"),
        )


class CurrentAssessmentResponseView(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AssessmentResponseSerializer

    def get_queryset(self):
        # TODO change request
        return AssessmentResponse.objects.filter(
            assessment__participations__in=Participation.objects.filter_available(
                self.request.user, timezone.now()
            ),
        )


class ExpertView(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name__in=["Experts"])


class AssessmentAddExpertView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, assessment_id):
        assessment = Assessment.objects.get(id=assessment_id)
        expert = User.objects.get(id=request.data.get("expert_id"))
        if not expert.is_expert:
            return RestResponse(status=status.HTTP_400_BAD_REQUEST)
        assessment.experts.add(expert)
        assessment.assessment_type = AssessmentType.objects.get(
            assessment_type=ManagedAssessmentType.WITH_EXPERT.value
        )
        consent_condition_of_sales(
            assessment, request.data.get("conditions_of_sale_consent")
        )
        assessment.save()

        serializer = AssessmentSerializer(assessment)
        return RestResponse(serializer.data, status=status.HTTP_200_OK)


class CompletedQuestionsInitializationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, assessment_id):
        assessment = Assessment.objects.get(
            id=assessment_id, initiated_by_user=request.user
        )
        assessment.is_initialization_questions_completed = True
        assessment.save()

        serializer = AssessmentSerializer(assessment)
        return RestResponse(serializer.data, status=status.HTTP_200_OK)


class AssessmentScoreView(APIView):
    # Cache page everyday
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, assessment_id):
        scores: Dict[str, Dict[str, float]] = get_scores_by_assessment_pk(assessment_id)
        return RestResponse(scores, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_chart_data(request, assessment_id, question_id):
    question = Question.objects.get(id=question_id)

    data = (
        CHART_DATA_FN_BY_QUESTION_TYPE[question.type](question, assessment_id)
        if CHART_DATA_FN_BY_QUESTION_TYPE.get(question.type)
        else None
    )

    return RestResponse(
        {
            "id": question.id,
            "assessment_id": assessment_id,
            "type": question.type,
            "data": data,
        },
    )
