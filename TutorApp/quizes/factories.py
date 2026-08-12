import factory

from TutorApp.courses.tests.factories import SectionFactory
from TutorApp.quizes.models import Quiz


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    section = factory.SubFactory(SectionFactory)
    title = factory.Faker("sentence", nb_words=3)
