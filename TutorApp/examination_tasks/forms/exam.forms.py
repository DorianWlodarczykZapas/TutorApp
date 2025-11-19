from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Exam


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "exam_type",
            "subject",
            "year",
            "month",
            "tasks_link",
            "solutions_link",
            "tasks_count",
            "level_type",
        ]
        labels = {
            "exam_type": _("Exam Type"),
            "subject": _("Subject"),
            "year": _("Year"),
            "month": _("Month"),
            "tasks_link": _("Tasks link"),
            "solutions_link": _("Solutions link"),
            "tasks_count": _("Number of tasks"),
            "level_type": _("Exam level"),
        }
