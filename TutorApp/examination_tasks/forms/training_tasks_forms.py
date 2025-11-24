from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import TrainingTask


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
