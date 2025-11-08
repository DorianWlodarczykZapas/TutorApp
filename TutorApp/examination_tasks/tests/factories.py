import factory
from factory.django import DjangoModelFactory

from ..choices import (
    LEVEL_CHOICES,
    MONTH_CHOICES,
    YEAR_CHOICES,
    ExamTypeChoices,
    SchoolLevelChoices,
    SubjectChoices,
)
from ..models import Book, Exam, Section, Topic


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


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Faker("sentence", nb_words=3)
    author = factory.Faker("name", locale="pl_PL")
    publication_year = factory.Faker("random_int", min=2015, max=2024)
    school_level = SchoolLevelChoices.PRIMARY
    subject = 1
    grade = 1

    class Params:

        primary_school = factory.Trait(
            school_level=SchoolLevelChoices.PRIMARY,
            grade=factory.Faker("random_element", elements=[7, 8]),
        )

        high_school = factory.Trait(
            school_level=SchoolLevelChoices.HIGH_SCHOOL,
            grade=factory.Faker("random_element", elements=[1, 2, 3, 4]),
        )

        multi_grade = factory.Trait(grade=None)

        no_author = factory.Trait(author="", publication_year=None)


class SectionFactory(DjangoModelFactory):
    class Meta:
        model = Section

    book = factory.SubFactory(BookFactory)

    name = factory.Faker(
        "random_element",
        elements=[
            "Linear Equations",
            "Quadratic Equations",
            "Thermodynamics",
            "Kinematics",
            "Organic Chemistry",
            "Cell Biology",
            "World War II",
            "Renaissance",
            "Grammar Basics",
            "Reading Comprehension",
        ],
    )


class TopicFactory(DjangoModelFactory):
    class Meta:
        model = Topic

    section = factory.SubFactory(SectionFactory)

    name = factory.Faker(
        "random_element",
        elements=[
            "Conditional probability",
            "Vietes formulas",
            "Bernoullis diagram",
            "Binomial distribution",
            "Quadratic equations - delta",
            "Linear functions - graph",
            "Pythagorean theorem",
        ],
    )
