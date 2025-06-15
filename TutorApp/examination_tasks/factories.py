import factory
from datetime import datetime
from .models import Exam

class ExamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Exam

    year = factory.LazyFunction(lambda: datetime.now().year)
    month = factory.Iterator([c[0] for c in Exam.MONTH_CHOICES])
    tasks_link = factory.Faker("url")
    solutions_link = factory.Faker("url")
    tasks_count = factory.Faker("pyint", min_value=10, max_value=60)
    level_type = factory.Iterator([c[0] for c in Exam.LEVEL_CHOICES])
