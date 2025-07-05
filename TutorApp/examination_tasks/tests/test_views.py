from typing import Dict, Optional

from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from ..factories import ExamFactory
from ..models import Exam, MathMatriculationTasks
from ..views import SearchMatriculationTaskView

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

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_only_teacher_can_access(self):
        self.client.login(username="student", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_teacher_can_view_form(self):
        self.client.login(username="teacher", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Matriculation Task")

    def test_teacher_can_submit_valid_task(self):
        self.client.login(username="teacher", password="testpass123")
        data = {"exam": self.exam.pk, "task_id": 1, "category": 1}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            MathMatriculationTasks.objects.filter(exam=self.exam, task_id=1).exists()
        )

    def test_cannot_add_duplicate_task_to_exam(self):
        MathMatriculationTasks.objects.create(
            exam=self.exam, task_id=2, category=2, type=self.exam.level_type
        )
        self.client.login(username="teacher", password="testpass123")
        response = self.client.post(
            self.url, {"exam": self.exam.pk, "task_id": 2, "category": 2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            "form",
            None,
            ["Math matriculation tasks with this Exam and Task id already exists."],
        )


class SearchMatriculationTaskViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.exam1 = ExamFactory(year=2020, month=5, level_type=1)
        self.exam2 = ExamFactory(year=2021, month=6, level_type=2)

        self.task1 = MathMatriculationTasks.objects.create(
            exam=self.exam1, task_id=1, category=1, type=1
        )
        self.task2 = MathMatriculationTasks.objects.create(
            exam=self.exam1, task_id=2, category=2, type=1
        )
        self.task3 = MathMatriculationTasks.objects.create(
            exam=self.exam2, task_id=1, category=1, type=2
        )

        self.url = reverse("examination_tasks:search_tasks")
        self.view = SearchMatriculationTaskView()

    def _create_request(
        self, params: Optional[Dict[str, str]] = None
    ) -> RequestFactory:
        url = self.url
        if params:
            url += f"?{QueryDict('', mutable=True).update(params).urlencode()}"
        request = self.factory.get(url)
        request.user = self.user
        return request

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_get_queryset_with_no_filters(self):
        request = self._create_request()
        self.view.request = request

        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 3)
        self.assertIn(self.task1, queryset)
        self.assertIn(self.task2, queryset)
        self.assertIn(self.task3, queryset)

    def test_get_queryset_with_year_filter(self):
        request = self._create_request({"year": "2020"})
        self.view.request = request

        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.task1, queryset)
        self.assertIn(self.task2, queryset)
        self.assertNotIn(self.task3, queryset)

    def test_get_queryset_with_month_filter(self):
        request = self._create_request({"month": "6"})
        self.view.request = request

        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.task3, queryset)
        self.assertNotIn(self.task1, queryset)
        self.assertNotIn(self.task2, queryset)

    def test_get_queryset_with_level_filter(self):

        request = self._create_request({"level": "2"})
        self.view.request = request

        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.task3, queryset)
        self.assertNotIn(self.task1, queryset)
        self.assertNotIn(self.task2, queryset)

    def test_get_queryset_with_category_filter(self):
        request = self._create_request({"category": "2"})
        self.view.request = request

        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.task2, queryset)
        self.assertNotIn(self.task1, queryset)
        self.assertNotIn(self.task3, queryset)

    def test_get_queryset_with_multiple_filters(self):
        request = self._create_request({"year": "2020", "category": "1"})
        self.view.request = request

        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(self.task1, queryset)
        self.assertNotIn(self.task2, queryset)
        self.assertNotIn(self.task3, queryset)

    def test_get_queryset_with_invalid_filters(self):
        request = self._create_request(
            {"year": "invalid", "month": "13", "level": "99"}
        )
        self.view.request = request

        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 3)

    def test_get_context_data(self):
        request = self._create_request({"year": "2020"})
        self.view.request = request
        self.view.object_list = self.view.get_queryset()

        context = self.view.get_context_data()

        self.assertEqual(context["title"], "Search Tasks")
        self.assertEqual(context["filter"], {"year": "2020"})
        self.assertIn("task_contents", context)
        self.assertEqual(len(context["task_contents"]), 2)

    def test_pagination(self):
        for i in range(3, 15):
            MathMatriculationTasks.objects.create(
                exam=self.exam1, task_id=i, category=1, type=1
            )

        request = self._create_request()
        self.view.request = request
        self.view.paginate_by = 10

        queryset = self.view.get_queryset()
        self.assertEqual(queryset.count(), 15)

        context = self.view.get_context_data(object_list=queryset[:10])
        self.assertEqual(len(context["object_list"]), 10)
        self.assertTrue(context["is_paginated"])

        context = self.view.get_context_data(object_list=queryset[10:15])
        self.assertEqual(len(context["object_list"]), 5)

    def test_get_int_param_helper(self):
        self.assertEqual(self.view._get_int_param("123"), 123)
        self.assertEqual(self.view._get_int_param(""), None)
        self.assertEqual(self.view._get_int_param(None), None)
        self.assertEqual(self.view._get_int_param("invalid"), None)
