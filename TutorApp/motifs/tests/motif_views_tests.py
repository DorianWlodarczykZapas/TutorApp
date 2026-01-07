import unittest

from django.test import Client


class AddMotifViewTest(unittest.TestCase):
    """Tests for AddMotifView"""

    def setUp(self):
        """Runs before each test"""
        self.client = Client()

    def test_get_add_motif_page(self):
        """Test GET request to add motif page"""
        response = self.client.get("/motifs/add/")

        print(f"Status code: {response.status_code}")

        self.assertIsNotNone(response)
