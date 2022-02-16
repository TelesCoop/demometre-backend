from django import forms

from open_democracy_back.models import QuestionFilter, ResponseChoice


class QuestionFilterForm(forms.ModelForm):
    class Meta:
        model = QuestionFilter
        fields = (
            "conditional_question",
            "intersection_operator",
            "response_choices",
            "numerical_operator",
            "numerical_value",
            "boolean_response",
        )

    def __init__(self, questions_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["conditional_question"].queryset = questions_list
        self.fields["response_choices"].queryset = ResponseChoice.objects.none()
