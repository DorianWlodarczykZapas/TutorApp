from courses.models import Section, Topic
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget


class TopicForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section"].empty_label = _("Section Name")

    class Meta:
        model = Topic
        fields = ["section", "name"]
        labels = {
            "section": _("Section Name"),
            "name": _("Input Topic Name"),
        }

        widgets = {
            "section": ModelSelect2Widget(
                model=Section,
                search_fields=["name__icontains"],
                attrs={
                    "placeholder": _("Section Name"),
                    "data-placeholder": _("Section Name"),
                },
            ),
            "name": forms.TextInput(attrs={"placeholder": " "}),
        }
