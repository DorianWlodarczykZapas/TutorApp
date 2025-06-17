from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..factories import ExamFactory
from ..models import Exam

User = get_user_model()


class ExamCreateViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "a@b.com", "pass1234")
        self.user = User.objects.create_user("user", "u@b.com", "pass1234")
        self.client = Client()
        self.url = reverse("examination_tasks:exam_add")

    def test_get_as_admin(self):
        self.client.force_login(self.admin)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Add New Exam")

    def test_post_valid_as_admin_creates_and_redirects(self):
        self.client.force_login(self.admin)
        exam = ExamFactory.build()
        data = {
            "year": exam.year,
            "month": exam.month,
            "tasks_link": exam.tasks_link,
            "solutions_link": exam.solutions_link,
            "tasks_count": exam.tasks_count,
            "level_type": exam.level_type,
        }
        r = self.client.post(self.url, data)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Exam.objects.filter(year=exam.year, month=exam.month).exists())

    def test_post_invalid_data_shows_errors(self):
        self.client.force_login(self.admin)
        data = {
            "year": "",
            "month": "",
            "tasks_link": "invalid-url",
            "solutions_link": "invalid-url",
            "tasks_count": -1,
            "level_type": "",
        }
        r = self.client.post(self.url, data)
        self.assertEqual(r.status_code, 200)
        self.assertFormError(r, "form", "year", "This field is required.")
        self.assertFormError(r, "form", "month", "This field is required.")
        self.assertFormError(r, "form", "tasks_link", "Enter a valid URL.")
        self.assertFormError(r, "form", "solutions_link", "Enter a valid URL.")

    def test_access_forbidden_for_non_admin(self):
        self.client.force_login(self.user)
        r_get = self.client.get(self.url)
        r_post = self.client.post(self.url, {})
        self.assertIn(r_get.status_code, (403, 302))
        if r_get.status_code == 302:
            self.assertIn("/login/", r_get.url)
        self.assertIn(r_post.status_code, (403, 302))

    def test_access_forbidden_for_anonymous(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r.url)


class AddMatriculationTaskViewTests(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher", password="testpass123", role_type=2
        )
        self.student = User.objects.create_user(
            username="student", password="testpass123", role_type=1
        )
        self.exam = ExamFactory()

        self.url = reverse("add_matriculation_task")
