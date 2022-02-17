import json
from collections import defaultdict
from django.shortcuts import render
from open_democracy_back.forms import QuestionFilterForm
from django.db.models import Q

from open_democracy_back.models import Question, ResponseChoice


def question_filter_view(request):

    if request.method == "POST":
        question_id = request.POST.get("question")
        questions_list = Question.objects.filter(~Q(id=question_id)).prefetch_related(
            "response_choices"
        )
        filter_form = QuestionFilterForm(
            request.POST, question_id=question_id, questions_list=questions_list
        )
        # The queryset of response_choices was changed dynamically un js, filter_form use the initial queryset, so the selection is not valid
        filter_form.fields["response_choices"].queryset = ResponseChoice.objects.filter(
            question_id=request.POST.get("conditional_question")
        )
        if filter_form.is_valid():
            filter_form.save()
            # No redirection, the user can create several filters in a row

    else:
        question_id = request.GET.get("question_id")
        questions_list = Question.objects.filter(~Q(id=question_id)).prefetch_related(
            "response_choices"
        )
        filter_form = QuestionFilterForm(
            question_id=question_id, questions_list=questions_list
        )

    conditionals_questions = Question.objects.filter(
        questions_that_depend_on_me__question_id=question_id
    )

    questions_response_by_id = defaultdict(
        lambda: {"type": "", "min": 0, "max": 0, "responses": {}}
    )
    for question in questions_list:
        questions_response_by_id[question.id]["type"] = question.type
        questions_response_by_id[question.id]["min"] = question.min
        questions_response_by_id[question.id]["max"] = question.max
        for response_choice in question.response_choices.all():
            questions_response_by_id[question.id]["responses"][
                response_choice.id
            ] = response_choice.response_choice

    return render(
        request,
        "admin/question_filter.html",
        {
            "conditionals_questions": conditionals_questions,
            "questions_response_by_id": json.dumps(questions_response_by_id),
            "filter_form": filter_form,
        },
    )
