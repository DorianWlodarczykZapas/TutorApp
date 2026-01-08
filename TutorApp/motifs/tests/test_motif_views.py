from django.test import Client, TestCase

from TutorApp.users.factories import TeacherFactory


class AddMotifViewTest(TestCase):

    def setUp(self):

        self.client = Client()

    def test_get_add_motif_page(self):
        """Test GET request to add motif page"""
        response = self.client.get("/motifs/add/")

        self.assertEqual(response.status_code, 403)

    def test_can_teacher_access_page(self):
        """Test case that checks if teacher can access the page"""

        teacher = TeacherFactory()

        self.client.login(username=teacher.username, password="testpass123")

        response = self.client.get("/motifs/add/")

        self.assertEqual(response.status_code, 200)
