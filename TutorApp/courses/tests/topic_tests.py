from courses.models import Topic
from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class AddTopicTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("add_topic")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.section = SectionFactory.create()
        self.valid_data = {"section": self.section.pk, "name": "Viete's Formulas"}

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

    def test_add_topic(self):
        """Test case that adds topic"""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Topic.objects.filter(name="Viete's Formulas").exists())

    def test_add_topic_without_section(self):
        """Test case that adds topic without section"""
        self.valid_data["section"] = None
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Topic.objects.count(), 0)

    def test_add_topic_with_empty_name(self):
        """Test case that adds topic with empty topic name"""
        self.valid_data["name"] = ""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Topic.objects.count(), 0)
