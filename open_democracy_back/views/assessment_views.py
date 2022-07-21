import logging
from collections import defaultdict
from datetime import date
from typing import Dict

from django.db.models import Count, Q, Avg
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
    Participation,
    Question,
    ParticipationResponse,
    ResponseChoice,
    PercentageRange,
    ClosedWithScaleCategoryResponse,
    Category,
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
from open_democracy_back.utils import QuestionType

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
            experts__in=[self.request.user],
            royalty_payed=True,
        ).exclude(end_date__lt=timezone.now())


class AssessmentView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AssessmentSerializer
    queryset = Assessment.objects.all()


class CurrentAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_assessment = Assessment.objects.filter(
            participations__in=Participation.objects.filter_current_available(
                self.request.user, timezone.now()
            ),
        ).get()
        serializer = AssessmentSerializer(current_assessment)
        return RestResponse(serializer.data)


class AssessmentResponseView(
    mixins.ListModelMixin, UpdateOrCreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAssessmentAdminOrReadOnly]
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
    permission_classes = [IsAssessmentAdminOrReadOnly]
    serializer_class = AssessmentResponseSerializer

    def get_queryset(self):
        return AssessmentResponse.objects.filter(
            assessment__participations__in=Participation.objects.filter_current_available(
                self.request.user, timezone.now()
            ),
        )


class CompletedQuestionsInitializationView(APIView):
    permission_classes = [IsAssessmentAdminOrReadOnly]

    def patch(self, _, assessment_pk):
        assessment = Assessment.objects.get(id=assessment_pk)
        assessment.is_initialization_questions_completed = True
        assessment.save()

        serializer = AssessmentSerializer(assessment)
        return RestResponse(serializer.data, status=status.HTTP_200_OK)


class PublishedAssessmentsView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        assessments = Assessment.objects.filter(initialization_date__lte=timezone.now())
        return [
            assessment for assessment in assessments if assessment.published_results
        ]


class AssessmentScoreView(APIView):
    # Cache page everyday
    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, assessment_pk):
        scores: Dict[str, Dict[str, float]] = get_scores_by_assessment_pk(assessment_pk)
        return RestResponse(scores, status=status.HTTP_200_OK)


def get_chart_data_subjective_queryset(assessment_pk, prefix_queryset=""):
    prefix = f"{prefix_queryset}__" if prefix_queryset else ""

    return {
        f"{prefix}answered_by__is_unknown_user": False,
        f"{prefix}assessment_id": assessment_pk,
        f"{prefix}has_passed": False,
    }


def get_chart_data_objective_queryset(assessment_pk, prefix_queryset=""):
    prefix = f"{prefix_queryset}__" if prefix_queryset else ""

    return {
        f"{prefix}answered_by__is_unknown_user": False,
        f"{prefix}assessment_id": assessment_pk,
        f"{prefix}has_passed": False,
    }


def get_chart_data_of_boolean_question(question, assessment_pk):
    if question.objectivity == "objective":
        base_count = "assessmentresponses"
        base_queryset = get_chart_data_objective_queryset(assessment_pk, base_count)
    else:
        base_count = "participationresponses"
        base_queryset = get_chart_data_subjective_queryset(assessment_pk, base_count)

    result = (
        Question.filter(id=question.id)
        .annotate(
            count=Count(base_count),
            true=Count(
                base_count,
                filter=Q(
                    **base_queryset, participationresponses__boolean_response=True
                ),
            ),
            false=Count(
                base_count,
                filter=Q(
                    **base_queryset, participationresponses__boolean_response=False
                ),
            ),
        )
        .get()
    )
    return {
        "true": {"label": "Oui", "value": result.true},
        "false": {"label": "Non", "value": result.false},
        "count": result.count,
    }


def get_chart_data_of_choice_question(question, assessment_pk, choice_type):
    if question.objectivity == "objective":
        base_count = f"{choice_type}_assessmentresponses"
        base_queryset = get_chart_data_objective_queryset(assessment_pk, base_count)
        root_queryset = get_chart_data_objective_queryset(assessment_pk)
        model = AssessmentResponse
    else:
        base_count = f"{choice_type}_participationresponses"
        base_queryset = get_chart_data_subjective_queryset(assessment_pk, base_count)
        root_queryset = get_chart_data_subjective_queryset(assessment_pk)
        model = ParticipationResponse

    response_choices = ResponseChoice.objects.filter(question_id=question.id).annotate(
        count=Count(base_count, filter=Q(**base_queryset))
    )
    data = {}
    for response_choice in response_choices:
        data["value"][response_choice.id] = {
            "label": response_choice.response_choice,
            "value": response_choice.count,
        }

    data["count"] = model.objects.filter(
        **root_queryset, question_id=question.id
    ).count()


def get_chart_data_of_unique_choice_question(question, assessment_pk):
    return get_chart_data_of_choice_question(question, assessment_pk, "unique_choice")


def get_chart_data_of_multiple_choice_question(question, assessment_pk):
    return get_chart_data_of_choice_question(question, assessment_pk, "multiple_choice")


@api_view(["GET"])
def get_chart_data(request, assessment_pk, question_pk):
    question = Question.objects.get(id=question_pk)

    if question.type == QuestionType.BOOLEAN:
        data = get_chart_data_of_boolean_question(question, assessment_pk)
    elif question.type == QuestionType.UNIQUE_CHOICE:
        current_queryset = {
            "unique_choice_participationresponses__participation__user__is_unknown_user": False,
            "unique_choice_participationresponses__participation__assessment_id": 6,
            "unique_choice_participationresponses__has_passed": False,
        }
        current_queryset2 = {
            "participation__user__is_unknown_user": False,
            "participation__assessment_id": 6,
            "has_passed": False,
        }
        response_choices = ResponseChoice.objects.filter(
            question_id=question_pk
        ).annotate(
            count=Count(
                "unique_choice_participationresponses", filter=Q(**current_queryset)
            )
        )
        for response_choice in response_choices:
            data["value"][response_choice.id] = {
                "label": response_choice.response_choice,
                "value": response_choice.count,
            }

        data["count"] = ParticipationResponse.objects.filter(
            **current_queryset2, question_id=question_pk
        ).count()

    elif question.type == QuestionType.MULTIPLE_CHOICE:
        base = "multiple_choice_participationresponses"
        current_queryset = {
            f"{base}__participation__user__is_unknown_user": False,
            f"{base}__participation__assessment_id": 6,
            f"{base}__has_passed": False,
        }
        current_queryset2 = {
            "participation__user__is_unknown_user": False,
            "participation__assessment_id": 6,
            "has_passed": False,
        }
        response_choices = ResponseChoice.objects.filter(
            question_id=question_pk
        ).annotate(count=Count(base, filter=Q(**current_queryset)))
        for response_choice in response_choices:
            data["value"][response_choice.id] = {
                "label": response_choice.response_choice,
                "value": response_choice.count,
            }

        data["count"] = ParticipationResponse.objects.filter(
            **current_queryset2, question_id=question_pk
        ).count()
    elif question.type == QuestionType.PERCENTAGE:
        # base_queryset = {
        #     f"participation__user__is_unknown_user": False,
        #     f"participation__assessment_id": assessment_pk,
        #     f"has_passed": False,
        # }
        base_queryset = {
            f"answered_by__is_unknown_user": False,
            f"assessment_id": assessment_pk,
            f"has_passed": False,
        }
        result = AssessmentResponse.objects.filter(
            **base_queryset, question_id=question_pk
        ).aggregate(count=Count("id"), value=Avg("percentage_response"))

        data["value"] = {"label": "Pourcentage moyen", "value": result["value"]}
        data["count"] = result["count"]
        data["ranges"] = [
            {
                "id": percentage_range.id,
                "score": percentage_range.associated_score,
                "lower_bound": percentage_range.lower_bound,
                "upper_bound": percentage_range.upper_bound,
            }
            for percentage_range in PercentageRange.objects.filter(
                question_id=question_pk
            )
        ]
    elif question.type == QuestionType.CLOSED_WITH_SCALE:
        current_queryset = {
            "participation_response__participation__user__is_unknown_user": False,
            "participation_response__participation__assessment_id": assessment_pk,
            "participation_response__has_passed": False,
        }
        result = (
            ClosedWithScaleCategoryResponse.objects.filter(
                participation_response__question_id=question_pk, **current_queryset
            )
            .values("category_id", "response_choice_id")
            .annotate(count=Count("id"))
        )
        result_by_category_id = defaultdict(lambda: {})
        for item in result:
            result_by_category_id[item["category_id"]][
                item["response_choice_id"]
            ] = item["count"]

        response_choices = ResponseChoice.objects.filter(question_id=question_pk)
        for category in Category.objects.filter(question_id=question_pk):
            data[category.id] = {"label": category.category, "value": {}}
            for response_choice in response_choices:
                data[category.id]["value"][response_choice.id] = {
                    "label": response_choice.response_choice,
                    "value": result_by_category_id[category.id].get(
                        response_choice.id, 0
                    ),
                }
    return RestResponse(
        {
            "id": question.id,
            "assessment_pk": assessment_pk,
            "type": question.type,
            "data": data,
        },
    )
