from django.db.models import Q
from django.shortcuts import render

from open_democracy_back.models import Question
from open_democracy_back.utils import QuestionType


def get_percentage_range_line_error(question):
    ranges = []
    for percentage_range in question.percentage_ranges.all():
        if percentage_range.linearized_score is not None:
            continue
        ranges.append(
            f"{percentage_range.lower_bound} à {percentage_range.upper_bound}"
        )
    return ", ".join(ranges)


def get_response_choices_line_error(question):
    choices = []
    for response_choice in question.response_choices.all():
        if response_choice.linearized_score is not None:
            continue
        choices.append(response_choice.response_choice)
    return ", ".join(choices)


MISSING_SCORE_MAP = {
    QuestionType.UNIQUE_CHOICE.value: get_response_choices_line_error,  # type: ignore
    QuestionType.MULTIPLE_CHOICE.value: get_response_choices_line_error,  # type: ignore
    QuestionType.CLOSED_WITH_SCALE.value: get_response_choices_line_error,  # type: ignore
    QuestionType.PERCENTAGE.value: get_percentage_range_line_error,  # type: ignore
}


def anomaly(request):
    question_missing_scores = (
        (
            Question.objects.filter(profiling_question=False)
            .exclude(type=QuestionType.BOOLEAN)
            .filter(
                Q(
                    percentage_ranges__linearized_score__isnull=True,
                    type=QuestionType.PERCENTAGE,
                )
                | Q(
                    response_choices__linearized_score__isnull=True,
                    type__in=[
                        QuestionType.UNIQUE_CHOICE,
                        QuestionType.MULTIPLE_CHOICE,
                        QuestionType.CLOSED_WITH_SCALE,
                    ],
                )
            )
        )
        .prefetch_related("percentage_ranges", "response_choices")
        .distinct()
    )

    score_missing_list = []
    for question_missing_score in question_missing_scores:
        get_text_function = MISSING_SCORE_MAP[question_missing_score.type]
        score_missing_list.append(
            {
                "text": get_text_function(question_missing_score),
                "url": f"/admin/open_democracy_back/questionnairequestion/edit/{question_missing_score.id}/",
            }
        )

    return render(
        request,
        "admin/missing_score.html",
        {"score_missing_list": score_missing_list},
    )
