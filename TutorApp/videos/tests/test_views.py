from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class VideoCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("video_form")
        self.password = "testpass123"
        self.teacher = TeacherFactory(password=self.password)
        self.student = UserFactory(password=self.password)

    @patch("videos.views.UserService")
    def test_teacher_can_access_video_form(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "videos/video_form.html")

    @patch("videos.views.UserService")
    def test_student_cannot_access_video_form(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = False
        self.client.login(username=self.student.username, password=self.password)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")
