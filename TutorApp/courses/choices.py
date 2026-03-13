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


class SchoolLevelChoices(models.IntegerChoices):
    PRIMARY = 1, _("Primary School")
    SECONDARY = 2, _("Secondary School")


class DifficultyLevelChoices(models.IntegerChoices):
    EASY = 1, _("Easy")
    INTERMEDIATE = 2, _("Intermediate")
    ADVANCED = 3, _("Advanced")


class GradeChoices(models.IntegerChoices):
    PRIMARY_7 = 7, _("7th Grade - Primary")
    PRIMARY_8 = 8, _("8th Grade - Primary")
    SECONDARY_1 = 9, _("1st Year - Secondary")
    SECONDARY_2 = 10, _("2nd Year - Secondary")
    SECONDARY_3 = 11, _("3rd Year - Secondary")
    SECONDARY_4 = 12, _("4th Year - Secondary")


class SubjectChoices(models.IntegerChoices):
    MATH = 1, _("Mathematics")
    PHYSICS = 2, _("Physics")


class BookTypeChoices(models.IntegerChoices):
    TEXTBOOK = 1, _("Textbook")
    TASK_COLLECTION = 2, _("Task Collection")
    WORK_CARDS = 3, _("Work Cards")
