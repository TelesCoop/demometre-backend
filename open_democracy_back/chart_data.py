from collections import defaultdict
from typing import Dict, Callable

from django.db.models import Count, Avg, Q

from open_democracy_back.models import (
    ResponseChoice,
    Category,
    ClosedWithScaleCategoryResponse,
    AssessmentResponse,
    ParticipationResponse,
    Question,
    PercentageRange,
)
from open_democracy_back.utils import QuestionType


def get_chart_data_objective_queryset(assessment_id, prefix_queryset=""):
    prefix = f"{prefix_queryset}__" if prefix_queryset else ""

    return {
        f"{prefix}answered_by__is_unknown_user": False,
        f"{prefix}assessment_id": assessment_id,
        f"{prefix}has_passed": False,
    }


def get_chart_data_subjective_queryset(assessment_id, prefix_queryset=""):
    prefix = f"{prefix_queryset}__" if prefix_queryset else ""

    return {
        f"{prefix}participation__user__is_unknown_user": False,
        f"{prefix}participation__assessment_id": assessment_id,
        f"{prefix}has_passed": False,
    }


def get_chart_data_of_boolean_question(question, assessment_id):
    if question.objectivity == "objective":
        base_count = "assessmentresponses"
        base_queryset = get_chart_data_objective_queryset(assessment_id, base_count)
    else:
        base_count = "participationresponses"
        base_queryset = get_chart_data_subjective_queryset(assessment_id, base_count)

    result = (
        Question.objects.filter(id=question.id)
        .annotate(
            count=Count(base_count),
            true=Count(
                base_count,
                filter=Q(**base_queryset, **{f"{base_count}__boolean_response": True}),
            ),
            false=Count(
                base_count,
                filter=Q(**base_queryset, **{f"{base_count}__boolean_response": False}),
            ),
        )
        .get()
    )
    return {
        "true": {"label": "Oui", "value": result.true},
        "false": {"label": "Non", "value": result.false},
        "count": result.count,
    }


def get_chart_data_of_choice_question(question, assessment_id, choice_type):
    if question.objectivity == "objective":
        base_count = f"{choice_type}_assessmentresponses"
        base_queryset = get_chart_data_objective_queryset(assessment_id, base_count)
        root_queryset = get_chart_data_objective_queryset(assessment_id)
        model = AssessmentResponse
    else:
        base_count = f"{choice_type}_participationresponses"
        base_queryset = get_chart_data_subjective_queryset(assessment_id, base_count)
        root_queryset = get_chart_data_subjective_queryset(assessment_id)
        model = ParticipationResponse

    response_choices = ResponseChoice.objects.filter(question_id=question.id).annotate(
        count=Count(base_count, filter=Q(**base_queryset))
    )
    data = {"value": {}}
    for response_choice in response_choices:
        data["value"][response_choice.id] = {
            "label": response_choice.response_choice,
            "value": response_choice.count,
        }

    data["count"] = model.objects.filter(
        **root_queryset, question_id=question.id
    ).count()
    return data


def get_chart_data_of_unique_choice_question(question, assessment_id):
    return get_chart_data_of_choice_question(question, assessment_id, "unique_choice")


def get_chart_data_of_multiple_choice_question(question, assessment_id):
    return get_chart_data_of_choice_question(question, assessment_id, "multiple_choice")


def get_chart_data_of_percentage_question(question, assessment_id):
    if question.objectivity == "objective":
        base_queryset = get_chart_data_objective_queryset(assessment_id)
        model = AssessmentResponse
    else:
        base_queryset = get_chart_data_subjective_queryset(assessment_id)
        model = ParticipationResponse
    result = model.objects.filter(**base_queryset, question_id=question.id).aggregate(
        count=Count("id"), value=Avg("percentage_response")
    )

    return {
        "value": {"label": "Pourcentage moyen", "value": result["value"]},
        "count": result["count"],
        "ranges": [
            {
                "id": percentage_range.id,
                "score": percentage_range.associated_score,
                "lower_bound": percentage_range.lower_bound,
                "upper_bound": percentage_range.upper_bound,
            }
            for percentage_range in PercentageRange.objects.filter(
                question_id=question.id
            )
        ],
    }


def get_chart_data_of_closed_with_scale_question(question, assessment_id):
    if question.objectivity == "objective":
        base_count = "assessment_response"
        base_queryset = get_chart_data_objective_queryset(assessment_id, base_count)
        root_queryset = get_chart_data_objective_queryset(assessment_id)
        model = AssessmentResponse
    else:
        base_count = "participation_response"
        base_queryset = get_chart_data_subjective_queryset(assessment_id, base_count)
        root_queryset = get_chart_data_subjective_queryset(assessment_id)
        model = ParticipationResponse

    base_queryset[f"{base_count}__question_id"] = question.pk

    result = (
        ClosedWithScaleCategoryResponse.objects.filter(**base_queryset)
        .values("category_id", "response_choice_id")
        .annotate(count=Count("id"))
    )
    result_by_category_id = defaultdict(lambda: {})
    for item in result:
        result_by_category_id[item["category_id"]][item["response_choice_id"]] = item[
            "count"
        ]

    data = {
        "count": model.objects.filter(**root_queryset, question_id=question.id).count()
    }
    response_choices = ResponseChoice.objects.filter(question_id=question.id)
    for category in Category.objects.filter(question_id=question.id):
        data[category.id] = {"label": category.category, "value": {}}
        for response_choice in response_choices:
            data[category.id]["value"][response_choice.id] = {
                "label": response_choice.response_choice,
                "value": result_by_category_id[category.id].get(response_choice.id, 0),
            }
    return data


CHART_DATA_FN_BY_QUESTION_TYPE: Dict[str, Callable] = {
    QuestionType.BOOLEAN.value: get_chart_data_of_boolean_question,  # type: ignore
    QuestionType.UNIQUE_CHOICE.value: get_chart_data_of_unique_choice_question,  # type: ignore
    QuestionType.MULTIPLE_CHOICE.value: get_chart_data_of_multiple_choice_question,  # type: ignore
    QuestionType.PERCENTAGE.value: get_chart_data_of_percentage_question,  # type: ignore
    QuestionType.CLOSED_WITH_SCALE.value: get_chart_data_of_closed_with_scale_question,  # type: ignore
}
