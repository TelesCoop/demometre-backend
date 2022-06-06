import json
from collections import defaultdict
from django.shortcuts import render
from django.urls import reverse
from open_democracy_back.forms import ProfileDefinitionForm, QuestionRuleForm
from django.db.models import Q
from django.views.generic.edit import BaseDeleteView

from open_democracy_back.models import (
    ProfileType,
    ProfilingQuestion,
    Question,
    QuestionnaireQuestion,
    QuestionType,
    ResponseChoice,
)
from open_democracy_back.models.questionnaire_and_profiling_models import (
    ProfileDefinition,
    QuestionRule,
)


def get_question_response_by_question_id(question_list):
    questions_response_by_question_id = defaultdict(
        lambda: {"type": "", "responses": {}}
    )
    for question in question_list:
        questions_response_by_question_id[question.id]["type"] = question.type
        for response_choice in question.response_choices.all():
            questions_response_by_question_id[question.id]["responses"][
                response_choice.id
            ] = response_choice.response_choice
    return json.dumps(questions_response_by_question_id)


def get_data_for_creating_profile_definition(profile_type):
    data = {}
    data["questions_list"] = ProfilingQuestion.objects.filter(
        ~Q(type=QuestionType.OPEN) & ~Q(type=QuestionType.CLOSED_WITH_SCALE)
    ).prefetch_related("response_choices")
    data["profile_type"] = profile_type
    data["rules"] = ProfileDefinition.objects.filter(profile_type_id=profile_type.id)
    data["rules_intersection_operator"] = profile_type.rules_intersection_operator
    data["questions_response_by_question_id"] = get_question_response_by_question_id(
        data["questions_list"]
    )
    return data


def get_data_for_creating_question_rules(question):
    data = {}
    data["is_profiling_question"] = question.profiling_question
    question_instance = (
        ProfilingQuestion if data["is_profiling_question"] else QuestionnaireQuestion
    )
    data["other_questions_list"] = question_instance.objects.filter(
        ~Q(id=question.id)
        & ~Q(type=QuestionType.OPEN)
        & ~Q(type=QuestionType.CLOSED_WITH_SCALE)
    )
    if not data["is_profiling_question"]:
        data["other_questions_list"] = data["other_questions_list"].filter(
            criteria__marker__pillar=question.criteria.marker.pillar
        )
    data["other_questions_list"].prefetch_related("response_choices")
    data["question"] = question
    data["rules"] = QuestionRule.objects.filter(question_id=question.id)
    data["rules_intersection_operator"] = question.rules_intersection_operator
    data["questions_response_by_question_id"] = get_question_response_by_question_id(
        data["other_questions_list"]
    )
    return data


def create_question_rule_form(data):
    return QuestionRuleForm(
        question=data["question"],
        other_questions_list=data["other_questions_list"],
    )


def create_profile_definition_form(data):
    return ProfileDefinitionForm(
        profile_type=data["profile_type"],
        questions_list=data["questions_list"],
    )


def profile_intersection_operator_view(request, pk):
    profile_type = ProfileType.objects.get(id=pk)
    profile_type.rules_intersection_operator = request.POST.get("intersection-operator")
    profile_type.save()

    data = get_data_for_creating_profile_definition(profile_type)
    rule_form = create_profile_definition_form(data)

    return render(
        request,
        "admin/profile_definition.html",
        {
            "data": data,
            "rule_form": rule_form,
        },
    )


def question_intersection_operator_view(request, pk):
    question = Question.objects.get(id=pk)
    question.rules_intersection_operator = request.POST.get("intersection-operator")

    data = get_data_for_creating_question_rules(question)
    rule_form = create_question_rule_form(data)

    return render(
        request,
        "admin/question_rules.html",
        {
            "data": data,
            "rule_form": rule_form,
        },
    )


def hidrate_form_response_choices(request, rule_form):
    # The queryset of response_choices was changed dynamically un js, rule_form use the initial queryset, so the selection is not valid
    rule_form.fields["response_choices"].queryset = ResponseChoice.objects.filter(
        question_id=request.POST.get("conditional_question")
    )


def question_rules_view(request, pk):
    question = Question.objects.get(id=pk)
    data = get_data_for_creating_question_rules(question)

    if request.method == "POST":
        rule_form = QuestionRuleForm(
            request.POST,
            question=data["question"],
            other_questions_list=data["other_questions_list"],
        )

        if request.POST.get("conditional_question"):
            hidrate_form_response_choices(request, rule_form)

        if rule_form.is_valid():
            rule_form.save()
            # No redirection, the user can create several filters in a row
            rule_form = create_question_rule_form(data)

    else:
        rule_form = create_question_rule_form(data)

    return render(
        request,
        "admin/question_rules.html",
        {
            "data": data,
            "rule_form": rule_form,
        },
    )


def profile_definition_view(request, pk):
    profile_type = ProfileType.objects.get(id=pk)
    data = get_data_for_creating_profile_definition(profile_type)

    if request.method == "POST":
        rule_form = ProfileDefinitionForm(
            request.POST,
            profile_type=data["profile_type"],
            questions_list=data["questions_list"],
        )

        if request.POST.get("conditional_question"):
            hidrate_form_response_choices(request, rule_form)

        if rule_form.is_valid():
            rule_form.save()
            # No redirection, the user can create several filters in a row
            rule_form = create_profile_definition_form(data)

    else:
        rule_form = create_profile_definition_form(data)

    return render(
        request,
        "admin/profile_definition.html",
        {
            "data": data,
            "rule_form": rule_form,
        },
    )


class QuestionRuleView(BaseDeleteView):
    model = QuestionRule

    def get_object(self):
        return QuestionRule.objects.get(id=self.kwargs.get("rule_pk"))

    def get_success_url(self):
        return reverse("question-filter", kwargs={"pk": str(self.kwargs.get("pk"))})


class ProfileDefinitionView(BaseDeleteView):
    model = ProfileDefinition

    def get_object(self):
        return ProfileDefinition.objects.get(id=self.kwargs.get("rule_pk"))

    def get_success_url(self):
        return reverse(
            "profile-type-definition", kwargs={"pk": str(self.kwargs.get("pk"))}
        )
