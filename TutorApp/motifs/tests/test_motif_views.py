from django.test import Client, TestCase
from examination_tasks.tests.factories import SectionFactory

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

    def test_can_teacher_add_motif(self):
        """Test case that checks if teacher can add motif"""
        teacher = TeacherFactory()
        self.client.login(username=teacher.username, password="testpass123")

        section = SectionFactory()

        data = {
            "subject": 1,
            "section": section.pk,
            "content": "How to solve equation",
            "answer": "Step by step",
            "level_type": 1,
            "is_mandatory": True,
            "is_in_matriculation_sheets": True,
        }

        response = self.client.post("/motifs/add/", data=data)

        self.assertEqual(response.status_code, 302)

    def test_is_motif_saved_to_database(self):
        """Test case that checks if motif is saved to database"""

        teacher = TeacherFactory()
        self.client.login(username=teacher.username, password="testpass123")

        section = SectionFactory()
        number_of_motifs_before = Motif.objects.count()

        data = {
            "subject": 1,
            "section": section.pk,
            "content": "How to solve equation",
            "answer": "Step by step",
            "level_type": 1,
            "is_mandatory": True,
            "is_in_matriculation_sheets": True,

        }

        response = self.client.post("/motifs/add/", data=data)

        number_of_motifs_after = Motif.objects.count()

        self.assertEqual(number_of_motifs_after, number_of_motifs_before + 1)


    def test_if_student_can_add_motif(self):
        """Test case that checks if student can add motif"""

        student = UserFactory()

        section = SectionFactory()


        data = {
            "subject": 1,
            "section": section.pk,
            "content": "How to solve equation",
            "answer": "Step by step",
            "level_type": 1,
            "is_mandatory": True,
            "is_in_matriculation_sheets": True,
        }

        self.client.login(username=student.username, password="testpass123")

        response = self.client.post("/motifs/add/", data=data)

        self.assertEqual(response.status_code, 403)