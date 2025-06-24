from django.test import TestCase
from django.urls import reverse
from users.tests.factories import TeacherFactory, UserFactory


class QuizCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("quiz:add")
        self.password = "testpass123"
        self.teacher = TeacherFactory(password=self.password)
        self.student = UserFactory(password=self.password)
