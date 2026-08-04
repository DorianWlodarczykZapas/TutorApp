from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from quizes.models import Quiz
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
        self.success_url = reverse("quizes:quiz_list")

    def test_unauthorized_access(self) -> None:
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            "/accounts/login/?next=%s" % self.url,
            fetch_redirect_response=False,
        )

    def test_can_teacher_access(self) -> None:
        """
        Test case that checks if teacher can access adding quiz page
        """
        self.client.force_login(self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_can_student_access(self) -> None:
        """Test case that checks if student can access adding quiz page"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_valid_data_as_teacher(self) -> None:
        """Test case that post valid data as teacher"""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Quiz.objects.count(), 1)
