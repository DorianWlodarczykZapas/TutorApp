import factory
from courses.factories import SectionFactory, TopicFactory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from ..choices import (
    LEVEL_CHOICES,
    MONTH_CHOICES,
    YEAR_CHOICES,
    ExamTypeChoices,
    SubjectChoices,
)
from ..models import Exam, ExamTask


class ExamFactory(DjangoModelFactory):
    class Meta:
        model = Exam

    exam_type = factory.Faker(
        "random_element", elements=[choice[0] for choice in ExamTypeChoices.choices]
    )

    subject = factory.Faker(
        "random_element", elements=[choice[0] for choice in SubjectChoices.choices]
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


class ExamTaskFactory(DjangoModelFactory):
    class Meta:
        model = ExamTask

    exam = factory.SubFactory(ExamFactory)
    task_id = factory.Sequence(lambda n: n + 1)

    section = None
    topic = None

    task_screen = factory.django.FileField(
        filename=factory.LazyAttribute(lambda o: f"task_{o.task_id}.pdf"),
        data=b"%PDF-1.4 fake content",
    )

    task_content = factory.Faker("paragraph", locale="pl_PL")
    task_pages = "1"
    answer_pages = "10"

    @factory.post_generation
    def completed_by(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            if isinstance(extracted, int):

                User = get_user_model()
                for i in range(extracted):
                    user = User.objects.create_user(
                        username=f"user_{self.id}_{i}",
                        email=f"user_{self.id}_{i}@example.com",
                    )
                    self.completed_by.add(user)
            else:

                for user in extracted:
                    self.completed_by.add(user)

    class Params:

        categorized = factory.Trait(
            section=factory.SubFactory(SectionFactory),
            topic=factory.SubFactory(TopicFactory),
        )

        multipage = factory.Trait(
            task_pages=factory.Faker(
                "random_element", elements=["1-2", "2-3", "3-4", "5-7"]
            ),
            answer_pages=factory.Faker(
                "random_element", elements=["10-11", "12-13", "15-17"]
            ),
        )

        completed = factory.Trait(completed_by=2)

        math_task = factory.Trait(
            exam=factory.SubFactory(ExamFactory, subject=SubjectChoices.MATH),
            section=factory.SubFactory(
                SectionFactory,
                name="Quadratic Equations",
                book__subject=SubjectChoices.MATH,
            ),
            topic=factory.SubFactory(
                TopicFactory,
                name="Vietes formulas",
                section__book__subject=SubjectChoices.MATH,
            ),
            task_content="Solve quadratic equation",
        )
