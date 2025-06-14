from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Exam
from ..factories import ExamFactory

User = get_user_model()

class ExamCreateViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", email="a@b.com", password="pass1234")
        self.client = Client()
        self.client.force_login(self.admin)
        self.url = reverse('examination_tasks:exam_add')

    def test_get_returns_200_and_contains_form_title(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Exam")

    def test_post_creates_exam_and_redirects(self):
        exam = ExamFactory.build()
        data = {
            'year': exam.year,
            'month': exam.month,
            'tasks_link': exam.tasks_link,
            'solutions_link': exam.solutions_link,
            'tasks_count': exam.tasks_count,
            'level_type': exam.level_type,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Exam.objects.filter(year=exam.year, month=exam.month).exists()
        )
