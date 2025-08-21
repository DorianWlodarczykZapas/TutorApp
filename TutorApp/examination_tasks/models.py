from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

current_year = datetime.now().year
YEAR_CHOICES = [(y, str(y)) for y in range(2002, current_year + 1)]

MONTH_CHOICES = [
    (1, _("January")),
    (2, _("February")),
    (3, _("March")),
    (4, _("April")),
    (5, _("May")),
    (6, _("June")),
    (7, _("July")),
    (8, _("August")),
    (9, _("September")),
    (10, _("October")),
    (11, _("November")),
    (12, _("December")),
]

LEVEL_CHOICES = [
    (1, _("Basic")),
    (2, _("Extended")),
]


class Exam(models.Model):
    year = models.IntegerField(choices=YEAR_CHOICES)
    month = models.IntegerField(choices=MONTH_CHOICES)
    tasks_link = models.FileField(upload_to="exam_pdfs/")
    solutions_link = models.FileField(
        upload_to="exam_answers_pdfs/", blank=True, null=True
    )
    tasks_count = models.PositiveIntegerField(
        default=0, help_text=_("Number of tasks in this exam")
    )
    level_type = models.IntegerField(
        choices=LEVEL_CHOICES, default=1, help_text=_("Exam level: basic or extended")
    )

    class Meta:

        unique_together = ("year", "month", "level_type")
        ordering = ["-year", "-month", "-level_type"]

    def __str__(self):
        level_display = dict(LEVEL_CHOICES).get(self.level_type)
        month_display = dict(MONTH_CHOICES).get(self.month)
        return f"{month_display} {self.year} – {level_display.lower()}"


class MathMatriculationTasks(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="tasks")
    task_id = models.IntegerField()
    category = models.IntegerField(
        choices=[
            (1, _("Sequences")),
            (2, _("Proofs (Special products)")),
            (3, _("Proofs (Divisibility)")),
            (4, _("Quadratic function – Viète's formulas")),
            (5, _("Quadratic function – optimization")),
            (6, _("Quadratic function")),
            (7, _("Linear function")),
            (8, _("Rational functions (x in denominator)")),
            (9, _("Analytical geometry")),
            (10, _("Prisms")),
            (11, _("Limits")),
            (12, _("Spheres, cylinders and cones")),
            (13, _("Logarithms")),
            (14, _("Inequalities and equations")),
            (15, _("Reading function properties")),
            (16, _("Pyramids")),
            (17, _("Planimetry – quadrilaterals")),
            (18, _("Planimetry – triangles and circles")),
            (19, _("Derivative – optimization")),
            (20, _("Derivative")),
            (21, _("Powers")),
            (22, _("Probability")),
            (23, _("Percentages")),
            (24, _("Trigonometric equations and inequalities")),
            (25, _("Equations with absolute value")),
            (26, _("Statistics")),
            (27, _("Geometric series")),
            (28, _("Trigonometry")),
            (29, _("Systems of equations")),
            (30, _("Polynomials")),
            (31, _("Special product formulas")),
            (32, _("Non-standard tasks")),
        ]
    )

    content = models.TextField(
        blank=True,
        editable=False,
        help_text=_("The extracted content of the task from the PDF file."),
    )

    pages = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Page number(s) in the PDF, e.g., '5' or '5-6'."),
    )
    answer = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("The correct answer or solution to the task."),
    )

    completed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="completed_exam_tasks",
        blank=True,
    )

    class Meta:
        unique_together = ("exam", "task_id")
        ordering = ["exam", "task_id"]

    def __str__(self):
        return f"{self.exam} – Task {self.task_id}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa kategorii")

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TaskSource(models.Model):
    class SchoolLevel(models.TextChoices):
        PRIMARY = "primary", _("Szkoła podstawowa")
        SECONDARY = "secondary", _("Szkoła średnia")

    title = models.CharField(max_length=255, verbose_name="Tytuł")
    author = models.CharField(max_length=255, blank=True, verbose_name="Autor")
    publication_year = models.IntegerField(
        null=True, blank=True, verbose_name="Rok wydania"
    )
    school_level = models.CharField(
        max_length=20,
        choices=SchoolLevel.choices,
        default=SchoolLevel.SECONDARY,
        verbose_name="Poziom szkoły",
    )

    class Meta:
        verbose_name = "Źródło zadań"
        verbose_name_plural = "Źródła zadań"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Chapter(models.Model):
    source = models.ForeignKey(
        TaskSource,
        on_delete=models.CASCADE,
        related_name="chapters",
        verbose_name="Źródło",
    )
    title = models.CharField(max_length=255, verbose_name="Tytuł rozdziału")
    chapter_number = models.CharField(
        max_length=20, blank=True, verbose_name="Numer rozdziału"
    )

    class Meta:
        verbose_name = "Rozdział"
        verbose_name_plural = "Rozdziały"
        unique_together = ("source", "title")
        ordering = ["source", "chapter_number"]

    def __str__(self):
        return f"{self.source.title} - Rozdział: {self.title}"


class MathMatriculationTrainingTask(models.Model):
    class LevelType(models.IntegerChoices):
        EASY = 1, _("Łatwy")
        INTERMEDIATE = 2, _("Średni")
        ADVANCED = 3, _("Trudny")

    task_content = models.TextField(verbose_name="Treść zadania")
    answer = models.CharField(max_length=255, verbose_name="Odpowiedź")

    image = models.ImageField(
        upload_to="tasks_images/",
        null=True,
        blank=True,
        verbose_name="Rysunek do zadania (opcjonalnie)",
    )

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="Rozdział (opcjonalnie)",
        null=True,
        blank=True,
    )
    categories = models.ManyToManyField(
        Category, related_name="tasks", verbose_name="Kategorie tematyczne", blank=True
    )

    level_type = models.IntegerField(
        choices=LevelType.choices,
        default=LevelType.INTERMEDIATE,
        verbose_name="Poziom trudności",
    )
    done_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="completed_training_tasks",
        blank=True,
    )

    class Meta:
        verbose_name = "Zadanie treningowe"
        verbose_name_plural = "Zadania treningowe"

    def __str__(self):
        return self.task_content[:80] + "..."
