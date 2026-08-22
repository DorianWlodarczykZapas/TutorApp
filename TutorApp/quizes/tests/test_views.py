from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from quizes.models import Answer, Question, Quiz
from users.factories import TeacherFactory, UserFactory

from TutorApp.quizes.factories import QuizFactory


class AddQuizViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("quizes:add_quiz")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.section = SectionFactory.create()
        self.valid_data = {"title": "Sequences", "section": self.section.pk}
        self.template_name = "quizes/add_quiz.html"
        self.success_url = reverse("quizes:quiz_list")

    def test_unauthorized_access(self) -> None:
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            "/accounts/login/?next=%s" % self.url,
            fetch_redirect_response=False,
        )

    def test_can_teacher_access(self) -> None:
        """
        Test case that checks if teacher can access adding quiz page
        """
        self.client.force_login(self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_can_student_access(self) -> None:
        """Test case that checks if student can access adding quiz page"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_valid_data_as_teacher(self) -> None:
        """Test case that post valid data as teacher"""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Quiz.objects.count(), 1)
        quiz = Quiz.objects.first()
        self.assertEqual(quiz.title, self.valid_data["title"])
        self.assertEqual(quiz.section_id, self.valid_data["section"])

    def test_post_empty_title_quiz(self) -> None:
        """Test case that post empty title quiz"""
        self.client.force_login(self.teacher)
        invalid_data = {**self.valid_data, "title": ""}
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quiz.objects.count(), 0)

    def test_post_invalid_section(self) -> None:
        """Test case that post invalid section"""
        self.client.force_login(self.teacher)
        invalid_data = {**self.valid_data, "section": -1}
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quiz.objects.count(), 0)

    def test_student_post_data(self) -> None:
        """Test case that post valid data as student"""
        self.client.force_login(self.student)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Quiz.objects.count(), 0)


class AddQuestionViewTests(TestCase):
    def setUp(self) -> None:
        self.quiz = QuizFactory.create()
        self.url = reverse("quizes:add_question", kwargs={"quiz_pk": self.quiz.pk})
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.template_name = "quizes/add_question.html"

        self.valid_data = {
            "text": "What is the value of e?",
            "level_type": 1,
            "explanation": "2.7",
            "answer_set-TOTAL_FORMS": 4,
            "answer_set-INITIAL_FORMS": 0,
            "answer_set-MIN_NUM_FORMS": 0,
            "answer_set-MAX_NUM_FORMS": 10,
            "answer_set-0-text": "3.14",
            "answer_set-0-is_correct": False,
            "answer_set-1-text": "0",
            "answer_set-1-is_correct": False,
            "answer_set-2-text": "2.7",
            "answer_set-2-is_correct": True,
            "answer_set-3-text": "109",
            "answer_set-3-is_correct": False,
        }

    def test_unauthorized_access(self) -> None:
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            "/accounts/login/?next=%s" % self.url,
            fetch_redirect_response=False,
        )

    def test_can_student_access(self) -> None:
        """Test case that checks if student can access adding quiz page"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_can_teacher_access(self) -> None:
        """
        Test case that checks if teacher can access adding quiz page
        """
        self.client.force_login(self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_teacher_post_valid_data(self) -> None:
        """
        Test case that checks if teacher can add question
        """
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 4)
        self.assertEqual(Question.objects.filter(quiz_id=self.quiz.pk).count(), 1)
        self.assertRedirects(response, self.url)

    def test_teacher_post_data_without_text(self) -> None:
        """Test case that checks if teacher can post blank question"""
        self.client.force_login(self.teacher)
        invalid_data = self.valid_data.copy()
        invalid_data["text"] = ""
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 0)
        self.assertFormError(
            response.context["form"], "text", "This field is required."
        )
