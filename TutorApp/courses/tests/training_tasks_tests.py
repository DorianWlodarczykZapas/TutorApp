from courses.models import TrainingTask
from courses.tests.factories import SectionFactory, TrainingTaskFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory
from django.utils.translation import gettext as _

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

    def test_add_training_task_with_invalid_section(self):
        """Test case that adds training task with invalid section"""
        self.valid_data["section"] = 99999
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_without_section(self):
        """Test case that adds training task without section"""
        self.valid_data["section"] = ""
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 1)

    def test_add_training_task_with_level_zero(self):
        """Test case that adds training task with level 0"""
        self.valid_data["level"] = 0
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_negative_level(self):
        """Test case that adds training task with negative level"""
        self.valid_data["level"] = -1
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_answer_too_long(self):
        """Test case that adds training task with answer exceeding max_length"""
        self.valid_data["answer"] = "x" * 256
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)



class TrainingTaskListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("training_tasks_list")
        self.student = UserFactory.create(grade=1)
        self.book = BookFactory.create(grade=1)
        self.section = SectionFactory.create(book=self.book)
        self.task = TrainingTaskFactory.create(section=self.section)

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_access_page(self):
        """Test case that checks if access is working"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_completion_percentage_is_zero_when_no_tasks(self):
        """Test case about 0% progress"""
        self.task.delete()
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["completion_percentage"], 0)

    def test_completion_percentage_when_task_completed(self):
        """Test case about 100% progress"""
        self.task.completed_by.add(self.student)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["completion_percentage"], 100)

    def test_completion_percentage_partial(self):
        """Test case about 50% progress"""
        task2 = TrainingTaskFactory.create(section=self.section)
        self.task.completed_by.add(self.student)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["completion_percentage"], 50)

    def test_context_has_title(self):
        """Test case about context title"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["title"], _("Training Tasks"))


