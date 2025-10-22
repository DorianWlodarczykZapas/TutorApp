from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Book, Exam, ExamTask, Section, Topic, TrainingTask
from .services import ExamTaskDBService


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


class AddExamTaskForm(forms.ModelForm):
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

    section = forms.ChoiceField(
        choices=ExamTask._meta.get_field("section").choices,
        label=_("Task Section"),
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

    answer = forms.CharField(
        label=_("Answer Page Number(s)"),
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("e.g. 15 or 15-16")}
        ),
        help_text=_("Page number(s) for the answer in the solutions PDF."),
    )

    class Meta:
        model = ExamTask
        fields = ["exam", "task_id", "section", "pages", "answer"]

    def clean(self):
        cleaned_data = super().clean()
        exam = cleaned_data.get("exam")
        task_id = cleaned_data.get("task_id")

        if exam and task_id:
            missing_ids = ExamTaskDBService.get_missing_task_ids(exam)
            if task_id not in missing_ids:
                raise forms.ValidationError(
                    _("Task number %(num)s already exists or is invalid."),
                    params={"num": task_id},
                )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exam"].queryset = (
            ExamTaskDBService.get_exams_with_available_tasks()
        )

        if "exam" in self.data:
            try:
                exam_id = int(self.data.get("exam"))
                exam = Exam.objects.get(pk=exam_id)
                missing = ExamTaskDBService.get_missing_task_ids(exam)
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


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "publication_year",
            "school_level",
        ]
        labels = {
            "title": _("Book Title"),
            "author": _("Author"),
            "publication_year": _("Publication Year"),
            "school_level": _("School Level"),
        }


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
