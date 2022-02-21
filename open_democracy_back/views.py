import json
from collections import defaultdict
from django.shortcuts import render
from django.urls import reverse, resolve
from open_democracy_back.forms import RuleForm
from django.db.models import Q
from django.views.generic.edit import BaseDeleteView

from open_democracy_back.models import (
    ProfileType,
    ProfilingQuestion,
    Question,
    QuestionType,
    Rule,
    ResponseChoice,
)


def rules_definition_view(request, pk):
    current_url = resolve(request.path_info).url_name
    if current_url == "profile-type-definition":
        other_questions_list = ProfilingQuestion.objects.filter(
            ~Q(type=QuestionType.OPEN) & ~Q(type=QuestionType.CLOSED_WITH_RANKING)
        ).prefetch_related("response_choices")
        other_profile_types = ProfileType.objects.filter(~Q(id=pk))
        profile_type = ProfileType.objects.get(id=pk)
        question = None
        rules = Rule.objects.filter(profile_type_id=pk)
    else:
        other_questions_list = Question.objects.filter(
            ~Q(id=pk)
            & ~Q(type=QuestionType.OPEN)
            & ~Q(type=QuestionType.CLOSED_WITH_RANKING)
        ).prefetch_related("response_choices")
        other_profile_types = ProfileType.objects.all()
        profile_type = None
        question = Question.objects.get(id=pk)
        rules = Rule.objects.filter(question_id=pk)

    if request.method == "POST":
        rule_form = RuleForm(
            request.POST,
            question=question,
            profile_type=profile_type,
            other_questions_list=other_questions_list,
            other_profile_types=other_profile_types,
        )
        # The queryset of response_choices was changed dynamically un js, rule_form use the initial queryset, so the selection is not valid
        rule_form.fields["response_choices"].queryset = ResponseChoice.objects.filter(
            question_id=request.POST.get("conditional_question")
        )
        if rule_form.is_valid():
            rule_form.save()
            # No redirection, the user can create several filters in a row
            rule_form = RuleForm(
                question=question,
                profile_type=profile_type,
                other_questions_list=other_questions_list,
                other_profile_types=other_profile_types,
            )

    else:
        rule_form = RuleForm(
            question=question,
            profile_type=profile_type,
            other_questions_list=other_questions_list,
            other_profile_types=other_profile_types,
        )

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
        "admin/rules.html",
        {
            "question": question,
            "profile_type": profile_type,
            "rules": rules,
            "other_questions_response_by_id": json.dumps(
                other_questions_response_by_id
            ),
            "rule_form": rule_form,
        },
    )


class RuleView(BaseDeleteView):
    model = Rule

    def get_object(self):
        return Rule.objects.get(id=self.kwargs.get("rule_pk"))

    def get_success_url(self):
        if resolve(self.request.path_info).url_name == "delete-profile-type-definition":
            return reverse("profile-type-definition", args=(str(self.kwargs.get("pk"))))
        return reverse("question-filter", args=(str(self.kwargs.get("pk"))))
