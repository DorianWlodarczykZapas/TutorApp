from courses.models import Section
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from ..models import Quiz


class QuizForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section"].empty_label = _("Section Name")

    class Meta:
        model = Quiz
        fields = ["title", "section"]

        labels = {"title": _("Quiz Title"), "section": _("Subject Section")}

        widgets = {
            "section": ModelSelect2Widget(
                model=Section,
                search_fields=["name__icontains"],
                attrs={
                    "placeholder": _("Section Name"),
                    "data-placeholder": _("Section Name"),
                },
            ),
            "title": forms.TextInput(attrs={"placeholder": " "}),
        }
