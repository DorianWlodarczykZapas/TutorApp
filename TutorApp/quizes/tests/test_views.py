from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class AddQuizViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("quizes:add_quiz")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.section = SectionFactory.create()
        self.valid_data = {"title": "Sequences", "section": self.section.pk}
        self.template_name = "quizes/add_quiz.html"

    def test_unauthorized_access(self) -> None:
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_can_teacher_access(self) -> None:
        """
        Test case that checks if teacher can access adding quiz page
        """
        self.client.force_login(self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
