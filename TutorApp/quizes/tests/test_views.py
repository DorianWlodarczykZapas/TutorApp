from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class AddQuizViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("quizes:add_quiz")
        self.student = UserFactory()
        self.teacher = TeacherFactory()
        self.section = SectionFactory.create()
        self.valid_data = {"title": "Sequences", "section": self.section.pk}
