from datetime import datetime

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


class ExamTypeChoices(models.IntegerChoices):
    MATRICULATION = 1, _("Matriculation Exam")
    EIGHTH_GRADE = 2, _("Eighth Grade Exam")
