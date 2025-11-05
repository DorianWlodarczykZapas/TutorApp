import factory
from factory.django import DjangoModelFactory

from ..choices import (
    LEVEL_CHOICES,
    MONTH_CHOICES,
    YEAR_CHOICES,
    ExamTypeChoices,
    SubjectChoices,
)
from ..models import Exam


class ExamFactory(DjangoModelFactory):
    class Meta:
        model = Exam

    exam_type = factory.Faker(
        "random_element", elements=[choice[0] for choice in ExamTypeChoices.choices]
    )

    subject = factory.Faker(
        "random_element", elements=[choice[0] for choice in SubjectChoices]
    )

    year = factory.Faker("random_element", elements=[y[0] for y in YEAR_CHOICES])

    month = factory.Faker("random_element", elements=[m[0] for m in MONTH_CHOICES])

    tasks_link = factory.django.FileField(
        filename="exam_tasks.pdf", data=b"fake pdf content"
    )

    solutions_link = factory.django.FileField(
        filename="exam_solutions.pdf", data=b"fake solutions content"
    )

    tasks_count = factory.Faker("random_int", min=5, max=50)

    @factory.lazy_attribute
    def level_type(self):
        if self.exam_type == ExamTypeChoices.MATRICULATION:

            return factory.Faker(
                "random_element", elements=[choice[0] for choice in LEVEL_CHOICES]
            ).evaluate(None, None, {"locale": None})
        return None
