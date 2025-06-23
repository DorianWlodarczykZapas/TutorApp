from django.test import TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class VideoCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("video_form")
        self.password = "testpass123"
        self.teacher = TeacherFactory(password=self.password)
        self.student = UserFactory(password=self.password)
