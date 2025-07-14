from unittest.mock import patch

from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from quiz.models import Answer, Quiz
from users.tests.factories import TeacherFactory, UserFactory


class QuizCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("quiz:add")
        self.password = "testpass123"
        self.teacher = TeacherFactory(password=self.password)
        self.student = UserFactory(password=self.password)

    @patch("quiz.views.UserService")
    def test_teacher_can_access_quiz_create_view(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quiz/add_question_to_quiz.html")

    @patch("quiz.views.UserService")
    def test_student_gets_permission_denied(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = False
        self.client.login(username=self.student.username, password=self.password)

        with self.assertRaises(PermissionDenied):
            self.client.get(self.url)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/login/?next={self.url}")

    @patch("quiz.views.UserService")
    def test_valid_quiz_and_answers_create_objects(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        quiz_data = {
            "question": "What is 2 + 2?",
            "type": 1,
            "explanation": "Because 2 + 2 = 4.",
        }

        formset_data = {
            "answers-TOTAL_FORMS": "2",
            "answers-INITIAL_FORMS": "0",
            "answers-MIN_NUM_FORMS": "0",
            "answers-MAX_NUM_FORMS": "1000",
            "answers-0-text": "4",
            "answers-0-is_correct": "on",
            "answers-1-text": "5",
            "answers-1-is_correct": "",
        }

        data = {**quiz_data, **formset_data}

        response = self.client.post(self.url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 2)

        quiz = Quiz.objects.first()
        answers = quiz.answers.all()
        correct = [a for a in answers if a.is_correct]
        incorrect = [a for a in answers if not a.is_correct]

        self.assertEqual(len(correct), 1)
        self.assertEqual(len(incorrect), 1)
        self.assertEqual(correct[0].text, "4")

    @patch("quiz.views.UserService")
    def test_invalid_form_renders_with_errors(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        invalid_data = {
            "question": "",
            "type": "",
            "answers-TOTAL_FORMS": "1",
            "answers-INITIAL_FORMS": "0",
            "answers-MIN_NUM_FORMS": "0",
            "answers-MAX_NUM_FORMS": "1000",
            "answers-0-text": "",
            "answers-0-is_correct": "",
        }

        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "question", "To pole jest wymagane.")
        self.assertContains(response, "To pole jest wymagane", html=True)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)

    @patch("quiz.views.UserService")
    def test_valid_quiz_but_invalid_answers_returns_errors(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        quiz_data = {
            "question": "Sample question?",
            "type": 1,
            "explanation": "Explanation here.",
        }

        invalid_formset_data = {
            "answers-TOTAL_FORMS": "1",
            "answers-INITIAL_FORMS": "0",
            "answers-MIN_NUM_FORMS": "0",
            "answers-MAX_NUM_FORMS": "1000",
            "answers-0-text": "",
            "answers-0-is_correct": "",
        }

        data = {**quiz_data, **invalid_formset_data}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "To pole jest wymagane", html=True)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)

    @patch("quiz.views.UserService")
    def test_invalid_formset_management_data(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        data = {
            "question": "Test question?",
            "type": 1,
            "answers-TOTAL_FORMS": "not-a-number",
            "answers-INITIAL_FORMS": "0",
            "answers-MIN_NUM_FORMS": "0",
            "answers-MAX_NUM_FORMS": "1000",
            "answers-0-text": "A",
            "answers-0-is_correct": "on",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "ManagementForm data is missing or has been tampered with",
            html=False,
        )

    @patch("quiz.views.UserService")
    def test_context_contains_title(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        response = self.client.get(self.url)
        self.assertEqual(response.context["title"], "Add new quiz question")
