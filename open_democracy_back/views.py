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
    ResponseChoice,
    Rule,
)


def get_data_for_creating_rules(model_instance):
    data = {}
    if isinstance(model_instance, Question):
        data["other_questions_list"] = Question.objects.filter(
            ~Q(id=model_instance.id)
            & ~Q(type=QuestionType.OPEN)
            & ~Q(type=QuestionType.CLOSED_WITH_RANKING)
        ).prefetch_related("response_choices")
        data["other_profile_types"] = ProfileType.objects.all()
        data["profile_type"] = None
        data["question"] = model_instance
        data["rules_intersection_operator"] = data[
            "question"
        ].rules_intersection_operator
        data["rules"] = Rule.objects.filter(question_id=model_instance.id)
    elif isinstance(model_instance, ProfileType):
        data["other_questions_list"] = ProfilingQuestion.objects.filter(
            ~Q(type=QuestionType.OPEN) & ~Q(type=QuestionType.CLOSED_WITH_RANKING)
        ).prefetch_related("response_choices")
        data["other_profile_types"] = ProfileType.objects.filter(
            ~Q(id=model_instance.id)
        )
        data["profile_type"] = model_instance
        data["question"] = None
        data["rules_intersection_operator"] = data[
            "profile_type"
        ].rules_intersection_operator
        data["rules"] = Rule.objects.filter(profile_type_id=model_instance.id)

    questions_response_by_question_id = defaultdict(
        lambda: {"type": "", "min": 0, "max": 0, "responses": {}}
    )
    for other_question in data["other_questions_list"]:
        questions_response_by_question_id[other_question.id][
            "type"
        ] = other_question.type
        questions_response_by_question_id[other_question.id]["min"] = other_question.min
        questions_response_by_question_id[other_question.id]["max"] = other_question.max
        for response_choice in other_question.response_choices.all():
            questions_response_by_question_id[other_question.id]["responses"][
                response_choice.id
            ] = response_choice.response_choice
    data["questions_response_by_question_id"] = json.dumps(
        questions_response_by_question_id
    )

    return data


def create_rule_form(data):
    return RuleForm(
        question=data["question"],
        profile_type=data["profile_type"],
        other_questions_list=data["other_questions_list"],
        other_profile_types=data["other_profile_types"],
    )


def intersection_operator_view(request, pk):
    current_url = resolve(request.path_info).url_name
    if current_url == "profile-type-intersection-operator":
        profile_type = ProfileType.objects.get(id=pk)
        profile_type.rules_intersection_operator = request.POST.get(
            "intersection-operator"
        )
        profile_type.save()
        instance = profile_type
    else:
        question = Question.objects.get(id=pk)
        question.rules_intersection_operator = request.POST.get("intersection-operator")
        question.save()
        instance = question

    data = get_data_for_creating_rules(instance)
    rule_form = create_rule_form(data)

    return render(
        request,
        "admin/rules.html",
        {
            "data": data,
            "rule_form": rule_form,
        },
    )


def rules_definition_view(request, pk):
    current_url = resolve(request.path_info).url_name
    if current_url == "profile-type-definition":
        instance = ProfileType.objects.get(id=pk)
    else:
        instance = Question.objects.get(id=pk)

    data = get_data_for_creating_rules(instance)

    if request.method == "POST":
        rule_form = RuleForm(
            request.POST,
            question=data["question"],
            profile_type=data["profile_type"],
            other_questions_list=data["other_questions_list"],
            other_profile_types=data["other_profile_types"],
        )

        if request.POST.get("conditional_question"):
            # The queryset of response_choices was changed dynamically un js, rule_form use the initial queryset, so the selection is not valid
            rule_form.fields[
                "response_choices"
            ].queryset = ResponseChoice.objects.filter(
                question_id=request.POST.get("conditional_question")
            )

        if rule_form.is_valid():
            rule_form.save()
            # No redirection, the user can create several filters in a row
            rule_form = create_rule_form(data)

    else:
        rule_form = create_rule_form(data)

    return render(
        request,
        "admin/rules.html",
        {
            "data": data,
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
