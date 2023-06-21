from collections import defaultdict
from typing import TypedDict, List, DefaultDict, Dict, Callable, Any

import numpy as np
import pandas as pd
from django.db.models import Case, When, Value, IntegerField, Avg, FloatField, Max

from open_democracy_back.models import (
    SCORE_MAP,
    ParticipationResponse,
    AssessmentResponse,
)
from open_democracy_back.utils import QuestionType


class QuestionScore(TypedDict):
    question_id: str
    question__criteria_id: int
    question__criteria__marker_id: int
    question__criteria__marker__pillar_id: int
    score: float


class QuestionScoreAverage(TypedDict):
    question__criteria_id: int
    question__criteria__marker_id: int
    question__criteria__marker__pillar_id: int
    score: float
    count: int


def get_score_of_boolean_question(queryset) -> List[QuestionScore]:
    result = (
        queryset.filter(question__type=QuestionType.BOOLEAN)
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
            score=Case(
                When(avg__gte=0.5, then=Value(SCORE_MAP[2])),
                default=Value(SCORE_MAP[1]),
                output_field=FloatField(),
            ),
            # count=Count("question_id"),
        )
    )

    return list(result)


def get_score_of_unique_choice_question(queryset) -> List[QuestionScore]:
    result = (
        queryset.filter(question__type=QuestionType.UNIQUE_CHOICE)
        .exclude(unique_choice_response__linearized_score__isnull=True)
        .values(
            "question_id",
            "question__criteria_id",
            "question__criteria__marker_id",
            "question__criteria__marker__pillar_id",
        )
        .annotate(
            score=Avg("unique_choice_response__linearized_score"),
            # count=Count("question_id"),
        )
    )

    return list(result)


def get_score_of_multiple_choice_question(queryset) -> List[QuestionScore]:
    multiple_choice_scores = (
        queryset.filter(question__type=QuestionType.MULTIPLE_CHOICE)
        .annotate(
            multiple_choice_score_max=Max("multiple_choice_response__linearized_score")
        )
        .values(
            "question_id",
            "multiple_choice_score_max",
            "question__criteria_id",
            "question__criteria__marker_id",
            "question__criteria__marker__pillar_id",
        )
    )

    multiple_choice_score_dict: DefaultDict[str, QuestionScoreAverage] = defaultdict(
        lambda: QuestionScoreAverage(
            score=0,
            count=0,
            question__criteria_id=-1,
            question__criteria__marker_id=-1,
            question__criteria__marker__pillar_id=-1,
        )
    )
    for score in multiple_choice_scores:
        if isinstance(score["multiple_choice_score_max"], float):
            multiple_choice_score_dict[score["question_id"]]["score"] += score[
                "multiple_choice_score_max"
            ]
            multiple_choice_score_dict[score["question_id"]]["count"] += 1
            multiple_choice_score_dict[score["question_id"]][
                "question__criteria_id"
            ] = score["question__criteria_id"]
            multiple_choice_score_dict[score["question_id"]][
                "question__criteria__marker_id"
            ] = score["question__criteria__marker_id"]
            multiple_choice_score_dict[score["question_id"]][
                "question__criteria__marker__pillar_id"
            ] = score["question__criteria__marker__pillar_id"]

    result: List[QuestionScore] = []
    for key in multiple_choice_score_dict:
        result.append(
            QuestionScore(
                question_id=key,
                score=multiple_choice_score_dict[key]["score"]
                / multiple_choice_score_dict[key]["count"],
                question__criteria_id=multiple_choice_score_dict[key][
                    "question__criteria_id"
                ],
                question__criteria__marker_id=multiple_choice_score_dict[key][
                    "question__criteria__marker_id"
                ],
                question__criteria__marker__pillar_id=multiple_choice_score_dict[key][
                    "question__criteria__marker__pillar_id"
                ],
            )
        )

    return result


def get_score_of_percentage_question(queryset) -> List[QuestionScore]:
    percentage_responses = (
        queryset.filter(question__type=QuestionType.PERCENTAGE)
        .exclude(percentage_response=None)
        .prefetch_related("question__percentage_ranges", "question__criteria__marker")
    )

    percentage_scores_dict: DefaultDict[str, QuestionScoreAverage] = defaultdict(
        lambda: QuestionScoreAverage(
            score=0,
            count=0,
            question__criteria_id=-1,
            question__criteria__marker_id=-1,
            question__criteria__marker__pillar_id=-1,
        ),
        {},
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
            continue

        percentage_scores_dict[response.question_id]["score"] += score
        percentage_scores_dict[response.question_id]["count"] += 1
        percentage_scores_dict[response.question_id][
            "question__criteria_id"
        ] = response.question.criteria_id
        percentage_scores_dict[response.question_id][
            "question__criteria__marker_id"
        ] = response.question.criteria.marker_id
        percentage_scores_dict[response.question_id][
            "question__criteria__marker__pillar_id"
        ] = response.question.criteria.marker.pillar_id

    result: List[QuestionScore] = []
    for key in percentage_scores_dict:
        result.append(
            QuestionScore(
                question_id=key,
                score=percentage_scores_dict[key]["score"]
                / percentage_scores_dict[key]["count"],
                question__criteria_id=percentage_scores_dict[key][
                    "question__criteria_id"
                ],
                question__criteria__marker_id=percentage_scores_dict[key][
                    "question__criteria__marker_id"
                ],
                question__criteria__marker__pillar_id=percentage_scores_dict[key][
                    "question__criteria__marker__pillar_id"
                ],
            )
        )
    return result


def get_score_of_closed_with_scale_question(queryset) -> List[QuestionScore]:
    closed_with_scale_responses = queryset.filter(
        question__type=QuestionType.CLOSED_WITH_SCALE
    ).prefetch_related(
        "closed_with_scale_response_categories__response_choice",
        "question__criteria__marker",
    )

    score_by_question_id: DefaultDict[str, QuestionScoreAverage] = defaultdict(
        lambda: QuestionScoreAverage(
            score=0,
            count=0,
            question__criteria_id=-1,
            question__criteria__marker_id=-1,
            question__criteria__marker__pillar_id=-1,
        )
    )
    for closed_with_scale_response in closed_with_scale_responses:
        category_score: float = 0
        category_count: int = 0
        for (
            closed_with_scale_response_categorie
        ) in closed_with_scale_response.closed_with_scale_response_categories.all():
            response_choice = closed_with_scale_response_categorie.response_choice
            if response_choice and isinstance(response_choice.linearized_score, float):
                category_score += response_choice.linearized_score
                category_count += 1

        if category_count > 0:
            score_by_question_id[closed_with_scale_response.question_id][
                "score"
            ] += category_score / (category_count or 1)
            score_by_question_id[closed_with_scale_response.question_id]["count"] += 1
            score_by_question_id[closed_with_scale_response.question_id][
                "question__criteria_id"
            ] = closed_with_scale_response.question.criteria_id
            score_by_question_id[closed_with_scale_response.question_id][
                "question__criteria__marker_id"
            ] = closed_with_scale_response.question.criteria.marker_id
            score_by_question_id[closed_with_scale_response.question_id][
                "question__criteria__marker__pillar_id"
            ] = closed_with_scale_response.question.criteria.marker.pillar_id

    result: List[QuestionScore] = []
    for key in score_by_question_id:
        result.append(
            QuestionScore(
                question_id=key,
                score=score_by_question_id[key]["score"]
                / score_by_question_id[key]["count"],
                question__criteria_id=score_by_question_id[key][
                    "question__criteria_id"
                ],
                question__criteria__marker_id=score_by_question_id[key][
                    "question__criteria__marker_id"
                ],
                question__criteria__marker__pillar_id=score_by_question_id[key][
                    "question__criteria__marker__pillar_id"
                ],
            )
        )

    return result


def get_score_of_number_question(queryset) -> List[QuestionScore]:
    pass


SCORES_FN_BY_QUESTION_TYPE: Dict[str, Callable] = {
    QuestionType.BOOLEAN.value: get_score_of_boolean_question,  # type: ignore
    QuestionType.UNIQUE_CHOICE.value: get_score_of_unique_choice_question,  # type: ignore
    QuestionType.MULTIPLE_CHOICE.value: get_score_of_multiple_choice_question,  # type: ignore
    QuestionType.PERCENTAGE.value: get_score_of_percentage_question,  # type: ignore
    QuestionType.CLOSED_WITH_SCALE.value: get_score_of_closed_with_scale_question,  # type: ignore
    QuestionType.NUMBER.value: get_score_of_number_question,  # type: ignore
}


def get_criterias_score(df: pd.DataFrame) -> pd.Series:
    df_non_boolean = df[df.type != "boolean"]
    criteria_sum = df.groupby("criteria_id")["score"].sum()
    # replace 0 by 1 to avoid divide by 0
    criteria_count = (
        df_non_boolean.groupby("criteria_id")["score"].count().replace(0, 1)
    )
    return criteria_sum / criteria_count


def get_score_by_previous_score(
    df: pd.DataFrame, previous_score: pd.Series, previous: str, current: str
) -> pd.Series:
    current_id_by_previous_ids = (
        df[[previous, current]].drop_duplicates().set_index(previous)
    )
    current_id_by_previous_ids["score"] = previous_score
    return current_id_by_previous_ids.groupby(current)["score"].mean()


def get_markers_score_by_criterias_score(
    df: pd.DataFrame, criterias_score: pd.Series
) -> pd.Series:
    return get_score_by_previous_score(df, criterias_score, "criteria_id", "marker_id")


def get_pillars_score_by_markers_score(
    df: pd.DataFrame, markers_score: pd.Series
) -> pd.Series:
    return get_score_by_previous_score(df, markers_score, "marker_id", "pillar_id")


def get_scores_by_assessment_pk(assessment_pk: int) -> Dict[str, Dict[str, float]]:
    # We ignore responses of question that have not criterias
    participation_responses = (
        ParticipationResponse.objects.filter(
            participation__user__is_unknown_user=False,
            participation__assessment_id=assessment_pk,
            question__profiling_question=False,
        )
        .exclude(has_passed=True)
        .exclude(question__criteria=None)
    )

    assessment_responses = AssessmentResponse.objects.filter(
        answered_by__is_unknown_user=False,
        assessment_id=assessment_pk,
    ).exclude(has_passed=True)

    score_by_question_id: Dict[str, float] = {}
    df_dict: Dict[str, List[Any]] = {
        "question_id": [],
        "criteria_id": [],
        "marker_id": [],
        "pillar_id": [],
        "score": [],
        "type": [],
    }
    for question_type in [
        QuestionType.BOOLEAN,
        QuestionType.UNIQUE_CHOICE,
        QuestionType.MULTIPLE_CHOICE,
        QuestionType.PERCENTAGE,
        QuestionType.CLOSED_WITH_SCALE,
    ]:
        question_type_scores = SCORES_FN_BY_QUESTION_TYPE[question_type.value](  # type: ignore
            participation_responses
        )

        question_type_scores.extend(
            SCORES_FN_BY_QUESTION_TYPE[question_type.value](  # type: ignore
                assessment_responses
            )
        )
        for score in question_type_scores:
            score_by_question_id[score["question_id"]] = score["score"]
            df_dict["question_id"].append(score["question_id"])
            df_dict["criteria_id"].append(score["question__criteria_id"])
            df_dict["marker_id"].append(score["question__criteria__marker_id"])
            df_dict["pillar_id"].append(score["question__criteria__marker__pillar_id"])
            df_dict["score"].append(score["score"])
            df_dict["type"].append(question_type.value)  # type: ignore

    df = pd.DataFrame.from_dict(df_dict)
    criterias_score = get_criterias_score(df)
    markers_score = get_markers_score_by_criterias_score(df, criterias_score)
    pillars_score = get_pillars_score_by_markers_score(df, markers_score)

    return {
        "by_question_id": score_by_question_id,
        "by_criteria_id": dict(criterias_score.replace({np.nan: None})),
        "by_marker_id": dict(markers_score.replace({np.nan: None})),
        "by_pillar_id": dict(pillars_score.replace({np.nan: None})),
    }
