from datetime import datetime

import factory
from factory import SubFactory

from .models import Exam, MathMatriculationTasks


class ExamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Exam

    year = factory.LazyFunction(lambda: datetime.now().year)
    month = factory.Iterator([c[0] for c in Exam.MONTH_CHOICES])
    tasks_link = factory.Faker("url")
    solutions_link = factory.Faker("url")
    tasks_count = factory.Faker("pyint", min_value=10, max_value=60)
    level_type = factory.Iterator([c[0] for c in Exam.LEVEL_CHOICES])


class MathMatriculationTasksFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MathMatriculationTasks

    exam = SubFactory(ExamFactory)
    task_id = factory.Sequence(lambda n: n + 1)
    task_number = factory.Sequence(lambda n: n + 1)
    task_text = factory.Faker("paragraph")
    solution = factory.Faker("paragraph")
    points = factory.Faker("random_int", min=1, max=10)
