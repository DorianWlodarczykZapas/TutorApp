import os

from courses.models import Topic
from django.conf import settings
from django.db import models

from . import choices
from .choices import SubjectChoices


class Exam(models.Model):
    exam_type = models.IntegerField(
        choices=choices.ExamTypeChoices.choices,
        default=choices.ExamTypeChoices.MATRICULATION,
        verbose_name="Exam type",
    )
    subject = models.CharField(
        max_length=10, choices=SubjectChoices, verbose_name="Subject", default=1
    )
    year = models.IntegerField(choices=choices.YEAR_CHOICES)
    month = models.IntegerField(choices=choices.MONTH_CHOICES)
    tasks_link = models.FileField(upload_to="exam_pdfs/")
    solutions_link = models.FileField(
        upload_to="exam_answers_pdfs/", blank=True, null=True
    )
    tasks_count = models.PositiveIntegerField(
        default=0, help_text="Number of tasks in this exam"
    )
    level_type = models.IntegerField(
        choices=choices.LEVEL_CHOICES,
        null=True,
        blank=True,
        help_text="Exam level: basic or extended (Matriculation only)",
    )

    class Meta:
        unique_together = ("year", "month", "level_type", "exam_type")
        ordering = ["-year", "-month", "-exam_type", "-level_type"]

    def __str__(self):

        month_display = dict(choices.MONTH_CHOICES).get(self.month)
        type_display = self.get_exam_type_display()

        if self.exam_type == choices.ExamTypeChoices.MATRICULATION:

            level_display = dict(choices.LEVEL_CHOICES).get(self.level_type)
            level_str = f" – {level_display.lower()}" if level_display else ""
            return f"{type_display} {month_display} {self.year}{level_str}"

        return f"{type_display} {month_display} {self.year}"


def exam_task_upload_path(instance, filename):
    exam = instance.exam
    return os.path.join(
        "exam_tasks",
        str(exam.subject.name),
        str(exam.exam_type),
        str(exam.year),
        str(exam.month),
        f"zadanie_{instance.task_id}.pdf",
    )


class ExamTask(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="tasks")
    task_id = models.IntegerField()
    section = models.ForeignKey(
        "Section",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exam_tasks",
        verbose_name="Section",
    )
    task_screen = models.FileField(
        upload_to=exam_task_upload_path,
        null=False,
        blank=False,
        verbose_name="Task PDF",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="Topic",
        null=True,
        blank=True,
    )
    task_content = models.TextField(
        blank=True,
        help_text="The extracted content of the task from the PDF file.",
    )
    task_pages = models.CharField(
        max_length=20,
        blank=True,
        help_text="Page number(s) in the PDF, e.g., '5' or '5-6'.",
        verbose_name="Task Pages",
    )
    answer_pages = models.CharField(
        max_length=20,
        blank=True,
        help_text="Page number(s) in the PDF with the solution.",
        verbose_name="Answer Pages",
    )
    completed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="completed_exam_tasks",
        blank=True,
    )

    class Meta:
        verbose_name = "Exam Task"
        verbose_name_plural = "Exam Tasks"
        unique_together = ("exam", "task_id")
        ordering = ["exam", "task_id"]

    def __str__(self) -> str:
        return f"{self.exam} – Task {self.task_id}"
