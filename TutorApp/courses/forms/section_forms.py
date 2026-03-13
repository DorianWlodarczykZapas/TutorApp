from common.forms import TypedChoiceMixin
from courses.choices import GradeChoices, SubjectChoices
from courses.models import Section
from django import forms
from django.utils.translation import gettext_lazy as _


class SectionForm(TypedChoiceMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["subject"] = self._make_typed_choice(SubjectChoices, _("Subject"))
        self.fields["grade"] = self._make_typed_choice(GradeChoices, _("Grade"))

    class Meta:
        model = Section
        fields = ["grade", "subject", "name"]
        labels = {
            "name": _("Section Name"),
        }

        widgets = {
            "name": forms.TextInput(attrs={"placeholder": " "}),
        }
