from django import forms

from open_democracy_back.models import Rule, ResponseChoice


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = (
            "question",
            "profile_type",
            "conditional_question",
            "conditional_profile_type",
            "intersection_operator",
            "response_choices",
            "numerical_operator",
            "numerical_value",
            "boolean_response",
        )

    response_choices = forms.ModelMultipleChoiceField(
        queryset=ResponseChoice.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "vertical"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop("question")
        profile_type = kwargs.pop("profile_type")
        other_questions_list = kwargs.pop("other_questions_list")
        other_profile_types = kwargs.pop("other_profile_types")
        super().__init__(*args, **kwargs)
        self.fields["question"].initial = question
        self.fields["profile_type"].initial = profile_type
        self.fields["conditional_question"].queryset = other_questions_list
        self.fields["conditional_profile_type"].queryset = other_profile_types
