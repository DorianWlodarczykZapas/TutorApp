import factory
from courses.models import Book, Section, Topic
from examination_tasks.choices import SchoolLevelChoices
from factory.django import DjangoModelFactory

from TutorApp.examination_tasks.choices import DifficultyLevelChoices


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
            school_level=SchoolLevelChoices.choices,
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


class TrainingTaskFactory(DjangoModelFactory):
    class Meta:
        model = TrainingTask


    task_content = factory.Faker("paragraph")
    answer = factory.Faker("word")
    image = None
    section = factory.SubFactory(SectionFactory)
    level = DifficultyLevelChoices.INTERMEDIATE

    @factory.post_generation
    def completed_by_users(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.completed_by.add(*extracted)
