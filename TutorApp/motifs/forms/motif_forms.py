from courses.models import Section
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from ..models import Motif


class AddMotifForm(forms.ModelForm):
    """Form for creating and editing Motifs"""

    class Meta:
        model = Motif
        fields = "__all__"

        labels = {
            "subject": _("Subject"),
            "section": _("Section"),
            "level_type": _("Level type"),
            "content": _("Whole motif content"),
            "answer": _("Explanation about chosen motif"),
            "answer_picture": _('"Motif explanation picture if needed'),
            "is_in_matriculation_sheets": _("If exists in matriculation sheets"),
            "is_mandatory": _("Whether students must learn this motif"),
        }
        widgets = {
            "subject": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "section": ModelSelect2Widget(
                model=Section,
                search_fields=["name__icontains"],
                attrs={
                    "class": "form-control",
                    "data-placeholder": _("Select a section..."),
                },
            ),
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",  # ← Bootstrap
                    "placeholder": _("e.g., How to solve quadratic equations"),
                }
            ),
            "answer": forms.Textarea(
                attrs={
                    "rows": 10,
                    "class": "form-control",
                    "placeholder": _("Step-by-step explanation..."),
                }
            ),
            "level_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }
