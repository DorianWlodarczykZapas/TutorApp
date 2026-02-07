from courses.models import Topic
from django import forms
from django.utils.translation import gettext_lazy as _


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["section", "name"]
        labels = {
            "section": _("Section Name"),
            "name": _("Specific Topic"),
        }
