from django.test import Client, TestCase
from django.urls import reverse
from examination_tasks.choices import SchoolLevelChoices

from TutorApp.users.factories import TeacherFactory, UserFactory


class AddBookViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("add_book")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.valid_data = {
            "title": "Math for 8 grader",
            "author": "Jan Kowalski",
            "publication_year": 2022,
            "school_level": SchoolLevelChoices.PRIMARY,
            "subject": 1,
            "grade": 8,
        }

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 302)

    def test_can_student_access(self):
        """Test case that checks if student can access adding book page"""
        self.client.login(
            username=self.student.username, password=self.teacher.password
        )
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 403)
