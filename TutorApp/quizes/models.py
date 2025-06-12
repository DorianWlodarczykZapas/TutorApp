from django.db import models


class Quiz(models.Model):
    section = (
        (1, "Real numbers"),
        (2, "Language of mathematics"),
        (3, "Systems of equations"),
        (4, "Functons"),
        (5, "Linear function"),
        (6, "Planimetry"),
        (7, "Quadratic function"),
        (8, "Polynomials"),
        (9, "Measurable function"),
        (10, "Trigonometry"),
        (11, "Planimetry circles"),
        (12, "Exponential and logarithmic functions"),
        (13, "Trigonometric functions"),
        (14, "Analytical geometry"),
        (15, "Sequences"),
        (16, "Differential calculus"),
        (17, "Statistics"),
        (18, "Probability"),
        (19, "Stereometry"),
    )
    type = models.IntegerField(choices=section)
    question = models.CharField(max_length=255)
    question_picture = models.ImageField(
        upload_to="question_picture/", blank=True, null=True
    )
