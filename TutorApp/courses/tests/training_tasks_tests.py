from courses.models import TrainingTask
from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class AddTrainingTasksTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.url = reverse("add_training_tasks")
        self.section = SectionFactory.create()
        self.valid_data = {
            "task_content": "Solve this equation",
            "answer": "4",
            "level": 3,
            "section": self.section.pk,
        }

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_can_teacher_access(self):
        """
        Test case that checks if teacher can access adding topic page
        """
        self.client.force_login(self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_can_student_access(self):
        """Test case that checks if student can access adding topic page"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_add_training_task(self):
        """Test case that adds training task"""
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            TrainingTask.objects.filter(task_content="Solve this equation").exists()
        )

    def test_add_training_task_with_empty_content(self):
        """Test case that adds training task with empty content"""
        self.valid_data["task_content"] = ""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_empty_answer(self):
        """Test case that adds training task with empty answer"""
        self.valid_data["answer"] = ""
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_invalid_level(self):
        """Test case that adds training task with invalid level"""
        self.valid_data["level"] = 99
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_wrong_level_type(self):
        """Test case that adds training task with wrong level type"""
        self.valid_data["level"] = "a"
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)
