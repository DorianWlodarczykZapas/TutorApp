from courses.choices import (
    BookTypeChoices,
    DifficultyLevelChoices,
    GradeChoices,
    SchoolLevelChoices,
    SubjectChoices,
    TaskSourceChoices,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User


class Book(models.Model):

    title = models.CharField(max_length=255, verbose_name="Title")
    book_type = models.IntegerField(
        choices=BookTypeChoices.choices,
        verbose_name="Book Type",
    )
    authors = models.CharField(max_length=500, blank=True, verbose_name="Author")
    publication_year = models.IntegerField(
        null=True, blank=True, verbose_name="Publication Year"
    )
    school_level = models.IntegerField(
        choices=SchoolLevelChoices.choices,
        verbose_name="School Level",
    )
    subject = models.IntegerField(
        choices=SubjectChoices.choices, verbose_name="Subject", default=1
    )
    grade = models.IntegerField(
        choices=GradeChoices.choices,
        null=True,
        blank=True,
        verbose_name="Target Grade",
        help_text="Leave empty for books covering multiple grades",
    )

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["school_level", "grade", "subject", "title"]

    def __str__(self):
        grade_info = f" - {self.get_grade_display()}" if self.grade else ""
        return f"{self.title} - {self.get_book_type_display()} {grade_info} ({self.get_subject_display()})"


class Section(models.Model):
    grade = models.IntegerField(choices=GradeChoices.choices)
    subject = models.IntegerField(choices=SubjectChoices.choices)
    name = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"{self.name} - {self.get_subject_display()} - {self.get_grade_display()}"
        )


class Topic(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="topics", verbose_name="Section"
    )
    name = models.CharField(
        max_length=255, verbose_name="Topic name", help_text="Specific topic"
    )

    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        ordering = ["section", "name"]
        unique_together = ["section", "name"]

    def __str__(self):
        return f"{self.section} - {self.name}"


class TrainingTask(models.Model):
    task_content = models.TextField(
        verbose_name="Task Content",
        help_text=_("Use $...$ for inline math, e.g., $x=2$"),
    )
    answer = models.TextField(
        verbose_name="Answer", help_text=_("Use $...$ for inline math, e.g., $x=2$")
    )
    image = models.ImageField(
        upload_to="tasks_images/",
        null=True,
        blank=True,
        verbose_name="Task Image (optional)",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        related_name="courses",
        verbose_name="Chapter (optional)",
        null=True,
        blank=True,
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="training_tasks",
        verbose_name=_("Book"),
    )
    page_number = models.IntegerField(null=True, blank=True)

    level = models.IntegerField(
        choices=DifficultyLevelChoices.choices,
        verbose_name="Difficulty Level",
    )

    explanation_timestamp = models.ForeignKey(
        "videos.VideoTimestamp",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="training_tasks",
    )

    source = models.IntegerField(
        choices=TaskSourceChoices.choices,
        verbose_name="Task Source",
    )

    class Meta:
        verbose_name = "Training Task"
        verbose_name_plural = "Training Tasks"

    def clean(self):
        if self.source == TaskSourceChoices.BOOK:
            if not self.book:
                raise ValidationError(_("Book task requires a book."))
            if not self.page_number:
                raise ValidationError(_("Book task requires a page number."))

    def __str__(self):
        return self.task_content[:80] + "..."


class UserTaskCompletion(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    task = models.ForeignKey(
        TrainingTask,
        on_delete=models.CASCADE,
        verbose_name=_("Task"),
    )
    completed_at = models.DateTimeField(
        auto_now_add=False, default=None, null=True, blank=True
    )

    class Meta:
        unique_together = ["user", "task"]
        verbose_name = _("User Task Completion")
        verbose_name_plural = _("User Task Completions")

    def __str__(self):
        return f"{self.user} - {self.task.pk} - {self.completed_at}"
