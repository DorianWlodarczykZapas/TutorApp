from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class MatriculationTasks(models.Model):
    task_link = models.URLField(max_length=500, blank=True, null=True)
    answer_link = models.URLField(max_length=500, blank=True, null=True)
    year = models.IntegerField()
    month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    task_id = models.IntegerField()
    CATEGORY_CHOICES = [
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

    category = models.IntegerField(choices=CATEGORY_CHOICES)
    level = ((1, "Basic"), (2, "Extended"))
    type = models.IntegerField(choices=level)
    is_done = models.BooleanField(default=False)
