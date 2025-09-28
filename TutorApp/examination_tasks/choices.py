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


class TopicChoices(models.IntegerChoices):
    QUADRATIC_FUNCTION_VIETEA_FORMULAS = 1, _("Quadratic Function Vietea Formulas")


class SectionChoices(models.IntegerChoices):
    REAL_NUMBERS = 1, _("Real Numbers")
    MATHEMATICAL_LANGUAGE = 2, _("Mathematic Language")
    SYSTEMS_OF_EQUATIONS = 3, _("Systems of Equations")
    FUNCTIONS = 4, _("Functions")
    LINEAR_FUNCTION = 5, _("Linear Function")
    PLANE_GEOMETRY_PART1 = 6, _("Plane Geometry Part 1")
    QUADRATIC_FUNCTION = 7, _("Quadratic Function")
    APPLICATIONS_OF_QUADRATIC_EQUATION = 8, _("Applications of Quadratic Equation")
    POLYNOMIALS = 9, _("Polynomials")
    RATIONAL_FUNCTION = 10, _("Rational Function")
    TRIGONOMETRY = 11, _("Trigonometry")
    PLANE_GEOMETRY_PART2 = 12, _("Plane Geometry Part 2")
    EXPONENTIAL_AND_LOGARITHMIC_FUNCTION = 13, _("Exponential and Logarithmic Function")
    TRIGONOMETRIC_FUNCTIONS = 14, _("Trigonometric Functions")
    ANALYTIC_GEOMETRY = 15, _("Analytic Geometry")
    SEQUENCES = 16, _("Sequences")
    DIFFERENTIAL_CALCULUS = 17, _("Differential Calculus")
    STATISTICS = 18, _("Statistics")
    PROBABILITY_CALCULUS = 19, _("Probability Calculus")
    SOLID_GEOMETRY = 20, _("Solid Geometry")
    SOLIDS_OF_REVOLUTION = 21, _("Solid Revolution")
    NUMBER_AND_ACTIONS = 22, _("Number and Actions")
    ALGEBRAIC_EXPRESSIONS_AND_EQUATIONS = 23, _("Algebraic Expressions")
    GEOMETRIC_SHAPES_ON_A_PLANE = 24, _("Geometry Shape on A Plane")
    APPLICATIONS_OF_MATHEMATICS = 25, _("Applications of Mathematics")
    PRISMS_AND_PYRAMIDS = 26, _("Prisms and Pyramids")
    SYMMETRIES = 27, _("Symmetries")
    WHEELS_AND_CIRCLES = 28, _("Wheels and Circles")
    PROBABILITY_CALCULATION = 29, _("Probability")


class SchoolLevelChoices(models.TextChoices):
    PRIMARY = "primary", _("Primary School")
    SECONDARY = "secondary", _("Secondary School")


class DifficultyLevelChoices(models.IntegerChoices):
    EASY = 1, _("Easy")
    INTERMEDIATE = 2, _("Intermediate")
    ADVANCED = 3, _("Advanced")
