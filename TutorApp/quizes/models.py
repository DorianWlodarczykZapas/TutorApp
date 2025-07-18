from django.db import models
from django.utils.translation import gettext_lazy as _


class Quiz(models.Model):
    section = (
        (1, _("Real numbers")),
        (2, _("Language of mathematics")),
        (3, _("Systems of equations")),
        (4, _("Functions")),
        (5, _("Linear function")),
        (6, _("Planimetry")),
        (7, _("Quadratic function")),
        (8, _("Polynomials")),
        (9, _("Measurable function")),
        (10, _("Trigonometry")),
        (11, _("Planimetry circles")),
        (12, _("Exponential and logarithmic functions")),
        (13, _("Trigonometric functions")),
        (14, _("Analytical geometry")),
        (15, _("Sequences")),
        (16, _("Differential calculus")),
        (17, _("Statistics")),
        (18, _("Probability")),
        (19, _("Stereometry")),
    )
    type = models.IntegerField(choices=section)
    question = models.CharField(max_length=255)
    question_picture = models.ImageField(
        upload_to="question_picture/", blank=True, null=True
    )
    explanation = models.TextField(blank=True, null=True)
    explanation_picture = models.ImageField(
        upload_to="explanation_picture/", blank=True, null=True
    )


class Answer(models.Model):
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"
