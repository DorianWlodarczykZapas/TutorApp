from django.test import Client, TestCase


class AddMotifViewTest(TestCase):

    def setUp(self):

        self.client = Client()

    def test_get_add_motif_page(self):
        """Test GET request to add motif page"""
        response = self.client.get("/motifs/add/")

        self.assertEqual(response.status_code, 403)
