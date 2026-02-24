from django.test import Client, TestCase
from django.urls import reverse
from examination_tasks.choices import SchoolLevelChoices
from users.factories import TeacherFactory, UserFactory

from .models import Book


class AddBookViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("add_book")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.valid_data = {
            "title": "Math for 8 grader",
            "author": "Jan Kowalski",
            "publication_year": 2022,
            "school_level": SchoolLevelChoices.PRIMARY,
            "subject": 1,
            "grade": 8,
        }

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 302)

    def test_can_student_access(self):
        """Test case that checks if student can access adding book page"""
        self.client.force_login(self.student)
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 302)

    def test_can_teacher_access(self):
        """
        Test case that checks if teacher can access adding book page
        """
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 200)

    def test_add_book(self):
        """Test case that checks if book can be added"""
        self.client.force_login(self.teacher)
        response = self.client.post(reverse("add_book"), data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(title="Math for 8 grader").exists())

    def test_add_book_without_title(self):
        """Test case that checks if book without title can be added"""
        self.valid_data["title"] = None
        self.client.force_login(self.teacher)
        response = self.client.post(reverse("add_book"), data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 0)

    def test_add_book_with_wrong_grade(self):
        """Test case that checks if book with grade below minimum (7) can be added"""
        self.valid_data["grade"] = 4
        self.client.force_login(self.teacher)
        response = self.client.post(reverse("add_book"), data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 0)

    def test_add_book_with_letters_in_publication_year(self):
        """Test case that checks if book with wrong publication year can be added"""
        self.valid_data["publication_year"] = "apple"
        self.client.force_login(self.teacher)
        response = self.client.post(reverse("add_book"), data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 0)

    def test_add_book_with_non_existing_subject(self):
        """Test case that checks if book with non-existing subject can be added
        Available subjects are (1) - math, (2) - physics"""
        self.valid_data["subject"] = 4
        self.client.force_login(self.teacher)
        response = self.client.post(reverse("add_book"), data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 0)
