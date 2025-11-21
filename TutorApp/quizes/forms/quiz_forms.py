from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["title", "section"]

    labels = {"title": _("Quiz Title"), "section": _("Subject Section")}
