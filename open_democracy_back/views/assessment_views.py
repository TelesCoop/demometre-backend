import logging

from collections import defaultdict

from datetime import date

import numpy as np
import pandas as pd
import rollbar
from django.contrib.auth.models import User
from django.db.models import (
    Avg,
    Case,
    When,
    Value,
    IntegerField,
    Max,
    Count,
    FloatField,
)
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response as RestResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

from open_democracy_back import settings
from open_democracy_back.exceptions import ErrorCode, ValidationFieldError
from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin

from open_democracy_back.models import (
    Assessment,
    ParticipationResponse,
    QuestionType,
    SCORE_MAP,
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


class AssessmentView(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
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


#
# class QuestionScoreStrategy(ABC):
#     @abstractmethod
#     def is_question_response_type(self, rule, response: Response):
#         pass
#
#
# class UniqueChoiceStrategy(QuestionScoreStrategy):
#     def does_respect_rule(self, rule: ProfileDefinition, response: Response):
#         return response.unique_choice_response in rule.response_choices.all()
#
#
# class MultipleChoiceStrategy(QuestionStrategy):
#     def does_respect_rule(self, rule: ProfileDefinition, response: Response):
#         return any(
#             [
#                 response in rule.response_choices.all()
#                 for response in response.multiple_choice_response
#             ]
#         )
#
#
# class BooleanStrategy(QuestionStrategy):
#     def does_respect_rule(self, rule: ProfileDefinition, response: Response):
#         return response.boolean_response == rule.boolean_response
#
#
# class PercentageStrategy(QuestionStrategy):
#     def does_respect_rule(self, rule: ProfileDefinition, response: Response):
#         return NUMERICAL_OPERATOR_CONVERSION[rule.numerical_operator](
#             response.percentage_response, rule.numerical_value
#         )
#
#
# RULES_STRATEGY = {
#     "unique_choice": UniqueChoiceStrategy(),
#     "multiple_choice": MultipleChoiceStrategy(),
#     "boolean": BooleanStrategy(),
#     "percentage": PercentageStrategy(),
# }


class QuestionnaireScoreView(APIView):
    def get(self, request, assessment_pk):
        scores_by_question_type = {}
        assessment_participation_responses = ParticipationResponse.objects.filter(
            participation__assessment_id=assessment_pk,
            question__profiling_question=False,
        ).exclude(has_passed=True)
        # BOOLEAN
        scores_by_question_type[QuestionType.BOOLEAN] = (
            assessment_participation_responses.filter(
                question__type=QuestionType.BOOLEAN
            )
            .annotate(
                boolean_response_int=Case(
                    When(boolean_response=True, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .values(
                "question_id",
                "question__criteria_id",
                "question__criteria__marker_id",
                "question__criteria__marker__pillar_id",
            )
            .annotate(
                avg=Avg("boolean_response_int"),
                count=Count("question_id"),
                score=Case(
                    When(avg__gte=0.5, then=Value(SCORE_MAP[2])),
                    default=Value(SCORE_MAP[1]),
                    output_field=FloatField(),
                ),
            )
        )

        # UNIQUE_CHOICE
        # TODO create field to determine Zscore when score change and use it there
        scores_by_question_type[QuestionType.UNIQUE_CHOICE] = (
            assessment_participation_responses.filter(
                question__type=QuestionType.UNIQUE_CHOICE
            )
            .values(
                "question_id",
                "question__criteria_id",
                "question__criteria__marker_id",
                "question__criteria__marker__pillar_id",
            )
            .annotate(
                score=Avg("unique_choice_response__linearized_score"),
                count=Count("question_id"),
            )
        )

        # MULTIPLE_CHOICE
        # scores_by_question_type["multiple_choice_score"] = assessment_participation_responses.filter(question__type=QuestionType.MULTIPLE_CHOICE).annotate(multiple_choice_score_max=Greatest('multiple_choice_response__linearized_score')).values('question_id', 'multiple_choice_score_max').annotate(values=Avg('multiple_choice_score_max'))
        multiple_choice_scores = (
            assessment_participation_responses.filter(
                question__type=QuestionType.MULTIPLE_CHOICE
            )
            .annotate(
                multiple_choice_score_max=Max(
                    "multiple_choice_response__linearized_score"
                )
            )
            .values(
                "question_id",
                "multiple_choice_score_max",
                "question__criteria_id",
                "question__criteria__marker_id",
                "question__criteria__marker__pillar_id",
            )
        )

        multiple_choice_score_dict = defaultdict(
            lambda: {
                "score": 0,
                "count": 0,
                "question__criteria_id": None,
                "question__criteria__marker_id": None,
                "question__criteria__marker__pillar_id": None,
            }
        )
        for score in multiple_choice_scores:
            multiple_choice_score_dict[score["question_id"]]["score"] += (
                score["multiple_choice_score_max"]
                if isinstance(score["multiple_choice_score_max"], int)
                else 0
            )
            multiple_choice_score_dict[score["question_id"]][
                "question__criteria_id"
            ] = score["question__criteria_id"]
            multiple_choice_score_dict[score["question_id"]][
                "question__criteria__marker_id"
            ] = score["question__criteria__marker_id"]
            multiple_choice_score_dict[score["question_id"]][
                "question__criteria__marker__pillar_id"
            ] = score["question__criteria__marker__pillar_id"]
            multiple_choice_score_dict[score["question_id"]]["count"] += 1

        scores_by_question_type[QuestionType.PERCENTAGE.MULTIPLE_CHOICE] = []
        for key in multiple_choice_score_dict:
            scores_by_question_type[QuestionType.PERCENTAGE.MULTIPLE_CHOICE].append(
                {
                    "question_id": key,
                    "score": multiple_choice_score_dict[key]["score"]
                    / multiple_choice_score_dict[key]["count"],
                    "count": multiple_choice_score_dict[key]["count"],
                    "question__criteria_id": multiple_choice_score_dict[key][
                        "question__criteria_id"
                    ],
                    "question__criteria__marker_id": multiple_choice_score_dict[key][
                        "question__criteria__marker_id"
                    ],
                    "question__criteria__marker__pillar_id": multiple_choice_score_dict[
                        key
                    ]["question__criteria__marker__pillar_id"],
                }
            )
        # percentage
        percentage_responses = assessment_participation_responses.filter(
            question__type=QuestionType.PERCENTAGE
        ).prefetch_related("question__percentage_ranges", "question__criteria__marker")

        percentage_score_dict = defaultdict(
            lambda: {
                "score": 0,
                "count": 0,
                "question__criteria_id": None,
                "question__criteria__marker_id": None,
                "question__criteria__marker__pillar_id": None,
            }
        )
        for response in percentage_responses:
            score = None
            for percentage_range in response.question.percentage_ranges.all():
                if (
                    percentage_range.lower_bound
                    <= response.percentage_response
                    <= percentage_range.upper_bound
                ):
                    score = percentage_range.linearized_score
                    break
            if score is None:
                if hasattr(settings, "production"):
                    rollbar.report_message(
                        f"Response {response.id} of percentage question {response.question_id} don't have score",
                        "warning",
                    )
                continue

            percentage_score_dict[response.question_id]["score"] += score
            percentage_score_dict[response.question_id]["count"] += 1
            percentage_score_dict[response.question_id][
                "question__criteria_id"
            ] = response.question.criteria_id
            percentage_score_dict[response.question_id][
                "question__criteria__marker_id"
            ] = response.question.criteria.marker_id
            percentage_score_dict[response.question_id][
                "question__criteria__marker__pillar_id"
            ] = response.question.criteria.marker.pillar_id

        scores_by_question_type[QuestionType.PERCENTAGE.PERCENTAGE] = []
        for key in percentage_score_dict:
            scores_by_question_type[QuestionType.PERCENTAGE].append(
                {
                    "question_id": key,
                    "score": percentage_score_dict[key]["score"]
                    / percentage_score_dict[key]["count"],
                    "count": percentage_score_dict[key]["count"],
                    "question__criteria_id": percentage_score_dict[key][
                        "question__criteria_id"
                    ],
                    "question__criteria__marker_id": percentage_score_dict[key][
                        "question__criteria__marker_id"
                    ],
                    "question__criteria__marker__pillar_id": percentage_score_dict[key][
                        "question__criteria__marker__pillar_id"
                    ],
                }
            )

        score_by_question_id = {}
        df_dict = {}
        for question_type in [
            QuestionType.BOOLEAN,
            QuestionType.UNIQUE_CHOICE,
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.PERCENTAGE,
        ]:
            for score in scores_by_question_type[question_type]:
                score_by_question_id[score["question_id"]] = score["score"]
                df_dict[score["question_id"]] = score
                df_dict[score["question_id"]]["type"] = question_type

        df = pd.DataFrame.from_dict(df_dict).transpose()
        df = df.rename(
            columns={
                "question__criteria_id": "criteria_id",
                "question__criteria__marker_id": "marker_id",
                "question__criteria__marker__pillar_id": "pillar_id",
            }
        )
        boolean_df_by_criteria = (
            df[df.type == QuestionType.BOOLEAN]
            .groupby(
                [
                    "criteria_id",
                    "marker_id",
                    "pillar_id",
                ]
            )["score"]
            .sum()
            .reset_index()
            .rename(columns={"score": "boolean_score_sum"})
        )
        df = df[df.type != QuestionType.BOOLEAN]
        criteria_mean = (
            df.groupby(
                [
                    "criteria_id",
                    "marker_id",
                    "pillar_id",
                ]
            )
            .agg({"score": "sum", "question_id": "count"})
            .reset_index()
            .rename(columns={"question_id": "count", "score": "score_sum"})
        )
        criteria_mean_merge = criteria_mean.merge(
            boolean_df_by_criteria[["criteria_id", "boolean_score_sum"]],
            on="criteria_id",
            how="left",
        )
        criteria_mean_merge["boolean_score_sum"] = criteria_mean_merge[
            "boolean_score_sum"
        ].replace(np.nan, 0)
        criteria_mean_merge["score_sum_sum"] = (
            criteria_mean_merge["score_sum"] + criteria_mean_merge["boolean_score_sum"]
        )
        criteria_mean_merge["score"] = (
            criteria_mean_merge["score_sum_sum"] / criteria_mean_merge["count"]
        )

        marker_mean = (
            criteria_mean_merge.groupby(
                [
                    "marker_id",
                    "pillar_id",
                ]
            )["score"]
            .mean()
            .reset_index()
        )
        pillar_mean = marker_mean.groupby("pillar_id")["score"].mean().reset_index()

        scores = {
            "by_question_id": score_by_question_id,
            "by_criteria_id": dict(
                zip(criteria_mean_merge.criteria_id, criteria_mean_merge.score)
            ),
            "by_marker_id": dict(zip(marker_mean.marker_id, marker_mean.score)),
            "by_pillar_id": dict(zip(pillar_mean.pillar_id, pillar_mean.score)),
        }
        return RestResponse(scores, status=status.HTTP_200_OK)
