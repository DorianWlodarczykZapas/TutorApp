from courses.models import Book, Section, TrainingTask
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget
from videos.models import VideoTimestamp


class TrainingTaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section"].empty_label = _("Section Name")
        self.fields["book"].empty_label = _("Book Name")

    class Meta:
        model = TrainingTask
        fields = [
            "task_content",
            "answer",
            "image",
            "section",
            "level",
            "book",
            "page_number",
            "explanation_timestamp",
        ]
        labels = {
            "task_content": _("Task Content"),
            "answer": _("Answer"),
            "image": _("Task Image (optional)"),
            "section": _("Section (optional)"),
            "level": _("Difficulty Level"),
            "book": _("Book (optional)"),
            "page_number": _("Page Number"),
            "explanation_timestamp": _("Explanation Timestamp"),
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
            "section": ModelSelect2Widget(
                model=Section,
                search_fields=["name__icontains"],
                attrs={
                    "placeholder": _("Section Name"),
                    "data-placeholder": _("Section Name"),
                },
            ),
            "book": ModelSelect2Widget(
                model=Book,
                search_fields=["title__icontains"],
                attrs={
                    "placeholder": _("Book Name"),
                    "data-placeholder": _("Book Name"),
                },
            ),
            "page_number": forms.NumberInput(attrs={"placeholder": " "}),
            "explanation_timestamp": ModelSelect2Widget(
                model=VideoTimestamp,
                search_fields=["label__icontains", "video__title__icontains"],
                attrs={
                    "placeholder": _("Explanation Timestamp"),
                    "data-placeholder": _("Explanation Timestamp"),
                },
            ),
        }
