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

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_can_teacher_access(self):
        """
        Test case that checks if teacher can access adding section page
        """
        self.client.force_login(self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
