import json
from collections import defaultdict
from django.shortcuts import render
from open_democracy_back.forms import QuestionFilterForm
from django.db.models import Q

from open_democracy_back.models import Question


def question_filter_view(request):

    if request.method == "POST":
        filter_form = QuestionFilterForm(request.POST)
        if filter_form.is_valid():
            print("RESULT : ")
            print(request.POST)
            print(filter_form)
            print("TEST -- ")
            print(filter_form.cleaned_data.get("conditional_question"))
        # return HttpResponseRedirect("/admin/snippets/open_democracy_back/question/")

    # else :
    question_id = request.GET.get("question_id")
    conditionals_questions = Question.objects.filter(
        questions_that_depend_on_me__question_id=question_id
    )
    questions_list = Question.objects.filter(~Q(id=question_id)).prefetch_related(
        "response_choices"
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

    filter_form = QuestionFilterForm(questions_list=questions_list)
    # breakpoint()

    return render(
        request,
        "admin/question_filter.html",
        {
            "question_id": question_id,
            "conditionals_questions": conditionals_questions,
            "questions_response_by_id": json.dumps(questions_response_by_id),
            "filter_form": filter_form,
        },
    )
