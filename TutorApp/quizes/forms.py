from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Answer, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            "type",
            "question",
            "question_picture",
            "explanation",
            "explanation_picture",
        ]
        labels = {
            "type": _("Section"),
            "question": _("Question"),
            "question_picture": _("Question image"),
            "explanation": _("Explanation"),
            "explanation_picture": _("Explanation image"),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text", "is_correct"]
        labels = {
            "text": _("Answer"),
            "is_correct": _("Correct?"),
        }


AnswerFormSet = inlineformset_factory(
    Quiz,
    Answer,
    form=AnswerForm,
    extra=4,
    can_delete=False,
    min_num=2,
    validate_min=True,
)
