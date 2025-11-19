from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Exam, ExamTask, Section, Topic, TrainingTask
from .services import ExamTaskDBService


class ExamTaskBasicForm(forms.Form):
    """First part of add exam task about adding all necessary parameters"""

    exam = forms.ModelChoiceField(
        queryset=Exam.objects.none(),
        label=_("Select Exam"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    task_id = forms.IntegerField(
        label=_("Task Number"),
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("e.g. 1")}
        ),
    )

    section = forms.ModelChoiceField(
        queryset=Section.objects.all().order_by("book__title", "name"),
        required=False,
        label=_("Section (optional)"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    topic = forms.ModelChoiceField(
        queryset=Topic.objects.none(),
        required=False,
        label=_("Topic (optional)"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    task_pages = forms.CharField(
        label=_("Task Page(s)"),
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("e.g. 5 or 5-6")}
        ),
        help_text=_("Page number(s) in the PDF, e.g., '5' or '5-6'."),
    )

    answer_pages = forms.CharField(
        label=_("Answer Page(s)"),
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("e.g. 15 or 15-16")}
        ),
        help_text=_("Page number(s) in the solutions PDF."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["exam"].queryset = (
            ExamTaskDBService.get_exams_with_available_tasks()
        )

        if self.data.get("exam"):
            try:
                exam_id = int(self.data.get("exam"))
                exam = Exam.objects.get(pk=exam_id)
                missing = ExamTaskDBService.get_missing_task_ids(exam)
                self.fields["task_id"].help_text = _(
                    "Available task numbers: "
                ) + ", ".join(map(str, missing))
            except (Exam.DoesNotExist, ValueError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        exam = cleaned_data.get("exam")
        task_id = cleaned_data.get("task_id")
        task_pages = cleaned_data.get("task_pages")

        if exam and not exam.exam_file:
            raise forms.ValidationError(_("Selected exam has no PDF file attached."))

        if exam and task_id:
            if ExamTask.objects.filter(exam=exam, task_id=task_id).exists():
                raise forms.ValidationError(
                    _("Task %(task_id)s already exists for this exam.")
                    % {"task_id": task_id}
                )

        if task_pages:
            if not self._validate_page_format(task_pages):
                raise forms.ValidationError(_("Invalid page format. Use '5' or '5-6'."))

        return cleaned_data

    def _validate_page_format(self, pages: str) -> bool:
        """Method checking if pages has good format"""
        import re

        pattern = r"^\d+(-\d+)?$"
        return bool(re.match(pattern, pages.strip()))


class ExamTaskPreviewForm(forms.Form):
    """
    This form allows the user to see:
    - The path to the generated PDF (task_screen)
    - The extracted task text (task_content) – editable
    - Confirmation checkbox
    """

    task_screen = forms.CharField(
        label=_("Generated PDF Path"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": "readonly",
            }
        ),
        required=False,
        help_text=_("Path to the extracted task PDF file (automatically generated)."),
    )

    task_content = forms.CharField(
        label=_("Task Content (editable)"),
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": _("Extracted task content..."),
            }
        ),
        required=False,
        help_text=_("You can edit the extracted text before saving."),
    )

    confirm = forms.BooleanField(
        label=_("I confirm that the task preview is correct"),
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        error_messages={"required": _("You must confirm the preview before saving.")},
    )


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


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["book", "name"]
        labels = {
            "book": _("Book Title"),
            "name": _("Section Name"),
        }


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["section", "name"]
        labels = {
            "section": _("Section Name"),
            "name": _("Specific Topic"),
        }


class TrainingTaskForm(forms.ModelForm):
    class Meta:
        model = TrainingTask
        fields = ["task_content", "answer", "image", "section", "level"]
        labels = {
            "task_content": _("Task Content"),
            "answer": _("Answer"),
            "image": _("Task Image (optional)"),
            "section": _("Section (optional)"),
            "level": _("Difficulty Level"),
        }
        widgets = {
            "task_content": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": _("Enter the task content here..."),
                }
            ),
            "answer": forms.TextInput(
                attrs={"placeholder": _("Enter the correct answer...")}
            ),
        }
