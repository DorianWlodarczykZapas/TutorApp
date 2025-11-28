from django import forms
from django.utils.translation import gettext_lazy as _


class QuizStepForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        answers = question.answers.all()
        self.fields["selected_answers"] = forms.MultipleChoiceField(
            choices=[(answer.id, answer.text) for answer in answers],
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )


class QuizStartForm(forms.Form):
    QUESTION_CHOICES = [
        (10, _("10 questions")),
        (20, _("20 questions")),
        (50, _("50 questions")),
        ("all", _("All questions")),
    ]

    question_count = forms.ChoiceField(
        choices=QUESTION_CHOICES,
        widget=forms.RadioSelect,
        label=_("How many questions would you like?"),
        initial=10,
    )
