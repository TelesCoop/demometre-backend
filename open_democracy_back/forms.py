from django import forms
from django.core.exceptions import ValidationError

from open_democracy_back.models import Rule, ResponseChoice


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = (
            "question",
            "profile_type",
            "conditional_question",
            "conditional_profile_type",
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

    def clean(self):
        cd = self.cleaned_data
        if (cd["numerical_operator"] and not cd["numerical_value"]) or (
            not cd["numerical_operator"] and cd["numerical_value"]
        ):
            raise ValidationError(
                "numerical_operator and numerical_value must be defined together"
            )

        return cd
