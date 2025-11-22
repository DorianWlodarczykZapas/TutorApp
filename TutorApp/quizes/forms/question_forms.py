from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from ..models import Answer, Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "level_type", "picture", "explanation", "explanation_picture"]
        labels = {
            "text": _("Question Content"),
            "level_type": _("Level Type"),
            "picture": _("Illustration for the question"),
            "explanation": _("Explanation To The Question"),
            "explanation_picture": _("Explanation By Illustration To The Question"),
        }


AnswerFormSet = inlineformset_factory(
    Question, Answer, fields=["text", "is_correct"], extra=4
)
