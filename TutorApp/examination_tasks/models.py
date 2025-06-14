from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _


current_year = datetime.now().year
YEAR_CHOICES = [(y, str(y)) for y in range(2002, current_year + 1)]

MONTH_CHOICES = [
    (1, _("January")), (2, _("February")), (3, _("March")),
    (4, _("April")), (5, _("May")), (6, _("June")),
    (7, _("July")), (8, _("August")), (9, _("September")),
    (10, _("October")), (11, _("November")), (12, _("December")),
]

class Exam(models.Model):
    year = models.IntegerField(choices=YEAR_CHOICES)
    month = models.IntegerField(choices=MONTH_CHOICES)
    tasks_link = models.URLField(_("Tasks link"))
    solutions_link = models.URLField(_("Solutions link"))
    tasks_count = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of tasks in this exam")
    )

    LEVEL_CHOICES = [
        (1, _("Basic")),
        (2, _("Extended")),
    ]

    level_type = models.IntegerField(
        choices=LEVEL_CHOICES,
        default=1,
        help_text=_("Exam level: basic or extended")
    )

    class Meta:
        unique_together = ('year', 'month')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"Matura {self.month}/{self.year}"


class MathMatriculationTasks(models.Model):
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name='tasks'
    )
    task_id = models.IntegerField()
    category = models.IntegerField(
        choices=[
            (1, _("Sequences")), (2, _("Proofs (Special products)")),
            (3, _("Proofs (Divisibility)")), (4, _("Quadratic function – Viète's formulas")),
            (5, _("Quadratic function – optimization")), (6, _("Quadratic function")),
            (7, _("Linear function")), (8, _("Rational functions (x in denominator)")),
            (9, _("Analytical geometry")), (10, _("Prisms")), (11, _("Limits")),
            (12, _("Spheres, cylinders and cones")), (13, _("Logarithms")),
            (14, _("Inequalities and equations")), (15, _("Reading function properties")),
            (16, _("Pyramids")), (17, _("Planimetry – quadrilaterals")),
            (18, _("Planimetry – triangles and circles")), (19, _("Derivative – optimization")),
            (20, _("Derivative")), (21, _("Powers")), (22, _("Probability")),
            (23, _("Percentages")), (24, _("Trigonometric equations and inequalities")),
            (25, _("Equations with absolute value")), (26, _("Statistics")),
            (27, _("Geometric series")), (28, _("Trigonometry")),
            (29, _("Systems of equations")), (30, _("Polynomials")),
            (31, _("Special product formulas")), (32, _("Non-standard tasks")),
        ]
    )
    type = models.IntegerField(
        choices=[(1, _("Basic")), (2, _("Extended"))]
    )

    class Meta:
        unique_together = ('exam', 'task_id')
        ordering = ['exam', 'task_id']

    def __str__(self):
        return f"{self.exam} – Task {self.task_id}"


class MathMatriculationTrainingTasks(models.Model):
    category_type = models.IntegerField(choices=[
        (1, _("Real numbers")), (2, _("Language of mathematics")),
        (3, _("Systems of equations")), (4, _("Functions")),
        (5, _("Linear function")), (6, _("Planimetry")),
        (7, _("Quadratic function")), (8, _("Polynomials")),
        (9, _("Measurable function")), (10, _("Trigonometry")),
        (11, _("Planimetry circles")), (12, _("Exponential and logarithmic functions")),
        (13, _("Trigonometric functions")), (14, _("Analytical geometry")),
        (15, _("Sequences")), (16, _("Differential calculus")),
        (17, _("Statistics")), (18, _("Probability")), (19, _("Stereometry")),
    ])
    task_content = models.TextField()
    answer = models.CharField(max_length=100)
    level_type = models.IntegerField(
        choices=[(1, _("Easy")), (2, _("Intermediate")), (3, _("Advanced"))]
    )

    done_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='completed_matriculation_tasks',
        blank=True
    )

    def __str__(self):
        return f"{self.get_category_type_display()} – Level {self.level_type}"
