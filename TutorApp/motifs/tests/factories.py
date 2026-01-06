import factory
from examination_tasks.tests.factories import SectionFactory
from factory.django import DjangoModelFactory

from TutorApp.motifs.models import Motif


class MotifFactory(DjangoModelFactory):

    class Meta:
        model = Motif

    subject = factory.Iterator(["math", "physics", "it"])

    section = factory.SubFactory(SectionFactory)

    level_type = factory.Iterator([1, 2, None])

    content = factory.Faker("sentence", nb_words=6, locale="pl_PL")

    answer = factory.Faker("paragraph", nb_sentences=5, locale="pl_PL")

    answer_picture = None

    is_in_matriculation_sheets = False
    is_mandatory = True
