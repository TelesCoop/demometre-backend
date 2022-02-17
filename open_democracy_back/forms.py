from django import forms

from open_democracy_back.models import Question, QuestionFilter, ResponseChoice


class QuestionFilterForm(forms.ModelForm):
    class Meta:
        model = QuestionFilter
        fields = (
            "question",
            "conditional_question",
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
        question_id = kwargs.pop("question_id")
        questions_list = kwargs.pop("questions_list")
        super().__init__(*args, **kwargs)
        self.fields["question"].initial = Question.objects.get(id=question_id)
        self.fields["conditional_question"].queryset = questions_list
