from courses.models import Topic
from django import forms
from django.utils.translation import gettext_lazy as _


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
            "section": forms.Select(attrs={"placeholder": " "}),
            "name": forms.TextInput(attrs={"placeholder": " "}),
        }
