from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "section"]

    labels = {"title": _("Quiz Title"), "section": _("Subject Section")}


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
