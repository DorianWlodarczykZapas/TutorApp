from django.test import Client, TestCase
from django.urls import reverse


class AddBookViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 302)
