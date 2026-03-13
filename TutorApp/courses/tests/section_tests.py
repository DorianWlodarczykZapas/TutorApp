from courses.choices import GradeChoices, SubjectChoices
from courses.models import Section
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


class AddSectionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("courses:add_section")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.valid_data = {
            "grade": GradeChoices.PRIMARY_7,
            "subject": SubjectChoices.MATH,
            "name": "Quadratic Equation",
        }

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_can_teacher_access(self):
        """Test case that checks if teacher can access adding section page"""
        self.client.force_login(self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_can_student_access(self):
        """Test case that checks if student can access adding book page"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_add_section(self):
        """Test case that adds section"""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Section.objects.filter(name="Quadratic Equation").exists())

    def test_add_section_without_grade(self):
        """Test case that adds section without grade"""
        self.valid_data["grade"] = ""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Section.objects.count(), 0)

    def test_add_section_without_subject(self):
        """Test case that adds section without subject"""
        self.valid_data["subject"] = ""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Section.objects.count(), 0)

    def test_add_section_without_name(self):
        """Test case that adds section without name"""
        self.valid_data["name"] = ""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Section.objects.count(), 0)

    def test_add_section_with_too_long_name(self):
        """Test case that adds section with too long name"""
        self.valid_data["name"] = "x" * 256
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Section.objects.count(), 0)
