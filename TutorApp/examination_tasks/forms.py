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

    pages = forms.CharField(
        label=_("Page Number(s)"),
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("e.g. 5 or 5-6")}
        ),
        help_text=_("Page number(s) in the PDF, e.g., '5' or '5-6'."),
    )

    class Meta:
        model = MathMatriculationTasks
        fields = ["exam", "task_id", "category", "pages"]

    def clean(self):
        cleaned_data = super().clean()
        exam = cleaned_data.get("exam")
        task_id = cleaned_data.get("task_id")

        if exam and task_id:
            missing_ids = MatriculationTaskService.get_missing_task_ids(exam)
            if task_id not in missing_ids:
                raise forms.ValidationError(
                    _("Task number %(num)s already exists or is invalid."),
                    params={"num": task_id},
                )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exam"].queryset = (
            MatriculationTaskService.get_exams_with_available_tasks()
        )

        if "exam" in self.data:
            try:
                exam_id = int(self.data.get("exam"))
                exam = Exam.objects.get(pk=exam_id)
                missing = MatriculationTaskService.get_missing_task_ids(exam)
                self.fields["task_id"].help_text = _(
                    "Available task numbers: "
                ) + ", ".join(map(str, missing))
            except (Exam.DoesNotExist, ValueError):
                pass


class TaskSearchForm(forms.Form):
    """
    Form used to validate and clean the parameters of
    matrix task filtering. It is not linked to any model.
    """

    year = forms.IntegerField(required=False)
    month = forms.IntegerField(required=False)
    level = forms.IntegerField(required=False)
    category = forms.IntegerField(required=False)

    is_done = forms.NullBooleanField(required=False)
