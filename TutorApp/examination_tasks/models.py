from django.conf import settings
from django.db import models

from . import choices


class Exam(models.Model):
    exam_type = models.IntegerField(
        choices=choices.ExamTypeChoices.choices,
        default=choices.ExamTypeChoices.MATRICULATION,
        verbose_name="Exam type",
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
    topic = models.IntegerField(
        choices=choices.TopicChoices.choices,
        null=True,
        blank=True,
        verbose_name="Task Topic",
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

    def __str__(self):
        return f"{self.exam} – Task {self.task_id}"


class Section(models.Model):
    name = models.IntegerField(
        choices=choices.SectionChoices.choices,
        unique=True,
        verbose_name="Name",
    )

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()


class Book(models.Model):
    SUBJECT_CHOICES = [
        ("MATH", "Mathematics"),
        ("PHYSICS", "Physics"),
    ]

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
        max_length=10, choices=SUBJECT_CHOICES, verbose_name="Subject"
    )
    grade = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Suggested Grade",
        help_text="Suggested grade level (1-8 for primary, 1-4 for secondary)",
    )

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["school_level", "subject", "grade", "title"]
        unique_together = ["title", "school_level", "subject"]

    def __str__(self):
        grade_info = f" - Grade {self.grade}" if self.grade else ""
        return f"{self.title}{grade_info} ({self.get_subject_display()})"


class Chapter(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="chapters",
        verbose_name="Book",
    )
    title = models.CharField(max_length=255, verbose_name="Chapter Title")
    chapter_number = models.CharField(
        max_length=20, blank=True, verbose_name="Chapter Number"
    )

    class Meta:
        verbose_name = "Chapter"
        verbose_name_plural = "Chapters"
        unique_together = ("book", "title")
        ordering = ["book", "chapter_number"]

    def __str__(self):
        return f"{self.book.title} - Chapter: {self.title}"


class TrainingTask(models.Model):
    task_content = models.TextField(verbose_name="Task Content")
    answer = models.CharField(max_length=255, verbose_name="Answer")
    image = models.ImageField(
        upload_to="tasks_images/",
        null=True,
        blank=True,
        verbose_name="Task Image (optional)",
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        related_name="training_tasks",
        verbose_name="Chapter (optional)",
        null=True,
        blank=True,
    )
    sections = models.ManyToManyField(
        Section, related_name="training_tasks", verbose_name="Sections", blank=True
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
