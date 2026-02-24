from courses.tests.factories import BookFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class AddSectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("add_section")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.book = BookFactory.create()
        self.valid_data = {
            "book": self.book.pk,
            "name": "Quadratic Equation",
        }
