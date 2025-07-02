from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Exam, MathMatriculationTasks
from .services import MatriculationTaskService


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "year",
            "month",
            "tasks_link",
            "solutions_link",
            "tasks_count",
            "level_type",
        ]
        labels = {
            "year": _("Year"),
            "month": _("Month"),
            "tasks_link": _("Tasks link"),
            "solutions_link": _("Solutions link"),
            "tasks_count": _("Number of tasks"),
            "level_type": _("Exam level"),
        }


class AddMatriculationTaskForm(forms.ModelForm):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.none(),
        label=_("Select Exam"),
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": _("Select exam, e.g. May 2025"),
            }
        ),
    )

    task_id = forms.IntegerField(
        label=_("Task Number"),
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("e.g. 1")}
        ),
    )

    category = forms.ChoiceField(
        choices=MathMatriculationTasks._meta.get_field("category").choices,
        label=_("Task Category"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = MathMatriculationTasks
        fields = ["exam", "task_id", "category"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exam"].queryset = (
            MatriculationTaskService.get_exams_with_available_tasks()
        )
