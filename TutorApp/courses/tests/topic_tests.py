from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class AddTopicTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("add_topic")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.section = SectionFactory.create()
        self.valid_data = {"section": self.section.pk, "name": "Viete's Formulas"}
