from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Quiz


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
