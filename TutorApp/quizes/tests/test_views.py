from unittest.mock import patch

from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from users.tests.factories import TeacherFactory, UserFactory


class QuizCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("quiz:add")
        self.password = "testpass123"
        self.teacher = TeacherFactory(password=self.password)
        self.student = UserFactory(password=self.password)

    @patch("quiz.views.UserService")
    def test_teacher_can_access_quiz_create_view(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quiz/add_question_to_quiz.html")

    @patch("quiz.views.UserService")
    def test_student_gets_permission_denied(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = False
        self.client.login(username=self.student.username, password=self.password)

        with self.assertRaises(PermissionDenied):
            self.client.get(self.url)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")
