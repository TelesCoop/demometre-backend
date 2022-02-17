import json
from collections import defaultdict
from django.shortcuts import render
from django.urls import reverse
from open_democracy_back.forms import QuestionFilterForm
from django.db.models import Q
from django.views.generic.edit import BaseDeleteView

from open_democracy_back.models import Question, QuestionFilter, ResponseChoice


def question_filter_view(request, pk):
    other_questions_list = Question.objects.filter(~Q(id=pk)).prefetch_related(
        "response_choices"
    )

    if request.method == "POST":
        filter_form = QuestionFilterForm(
            request.POST, question_id=pk, other_questions_list=other_questions_list
        )
        # The queryset of response_choices was changed dynamically un js, filter_form use the initial queryset, so the selection is not valid
        filter_form.fields["response_choices"].queryset = ResponseChoice.objects.filter(
            question_id=request.POST.get("conditional_question")
        )
        if filter_form.is_valid():
            filter_form.save()
            # No redirection, the user can create several filters in a row

    else:
        filter_form = QuestionFilterForm(
            question_id=pk, other_questions_list=other_questions_list
        )

    question = Question.objects.get(id=pk)

    question_filters = QuestionFilter.objects.filter(question_id=pk)

    other_questions_response_by_id = defaultdict(
        lambda: {"type": "", "min": 0, "max": 0, "responses": {}}
    )
    for other_question in other_questions_list:
        other_questions_response_by_id[other_question.id]["type"] = other_question.type
        other_questions_response_by_id[other_question.id]["min"] = other_question.min
        other_questions_response_by_id[other_question.id]["max"] = other_question.max
        for response_choice in other_question.response_choices.all():
            other_questions_response_by_id[other_question.id]["responses"][
                response_choice.id
            ] = response_choice.response_choice

    return render(
        request,
        "admin/question_filter.html",
        {
            "question": question,
            "question_filters": question_filters,
            "other_questions_response_by_id": json.dumps(
                other_questions_response_by_id
            ),
            "filter_form": filter_form,
        },
    )


class QuestionFilterView(BaseDeleteView):
    model = QuestionFilter

    def get_object(self):
        return QuestionFilter.objects.get(id=self.kwargs.get("question_filter_pk"))

    def get_success_url(self):
        return reverse("filter", args=(str(self.kwargs.get("pk"))))
