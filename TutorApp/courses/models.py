from django.conf import settings
from django.db import models

from ..examination_tasks import choices
from ..examination_tasks.choices import GradeChoices, SubjectChoices


class Book(models.Model):

    title = models.CharField(max_length=255, verbose_name="Title")
    author = models.CharField(max_length=255, blank=True, verbose_name="Author")
    publication_year = models.IntegerField(
        null=True, blank=True, verbose_name="Publication Year"
    )
    school_level = models.CharField(
        max_length=20,
        choices=choices.SchoolLevelChoices.choices,
        verbose_name="School Level",
    )
    subject = models.CharField(
        max_length=10, choices=SubjectChoices, verbose_name="Subject", default=1
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
        return f"{self.title}{grade_info} ({self.get_subject_display()})"


class Section(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="Book",
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Section Name",
        help_text="e.g., 'Linear Equations', 'Thermodynamics', 'Kinematics'",
    )

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ["name"]

    def __str__(self):
        return f"{self.book.title} - {self.name}"


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
    task_content = models.TextField(verbose_name="Task Content")
    answer = models.CharField(max_length=255, verbose_name="Answer")
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

    level = models.IntegerField(
        choices=choices.DifficultyLevelChoices.choices,
        default=choices.DifficultyLevelChoices.INTERMEDIATE,
        verbose_name="Difficulty Level",
    )
    completed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="completed_training_tasks",
        blank=True,
    )

    class Meta:
        verbose_name = "Training Task"
        verbose_name_plural = "Training Tasks"

    def __str__(self):
        return self.task_content[:80] + "..."
