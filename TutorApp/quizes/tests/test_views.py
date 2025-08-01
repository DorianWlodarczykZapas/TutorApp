from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from quiz.forms import CategorySelectForm
from quiz.models import Answer, Quiz
from quiz.views import CategorySelectView
from users.tests.factories import TeacherFactory, UserFactory

from TutorApp.quizes.views import QuizCreateView

User = get_user_model()


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

    @patch("quiz.views.UserService")
    def test_quiz_with_no_correct_answer(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        data = {
            "question": "Which color is the sky?",
            "type": 1,
            "explanation": "It's blue on a clear day.",
            "answers-TOTAL_FORMS": "2",
            "answers-INITIAL_FORMS": "0",
            "answers-MIN_NUM_FORMS": "0",
            "answers-MAX_NUM_FORMS": "1000",
            "answers-0-text": "Red",
            "answers-0-is_correct": "",
            "answers-1-text": "Green",
            "answers-1-is_correct": "",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)
        self.assertContains(response, "Musisz zaznaczyć poprawną odpowiedź", html=False)

    @patch("quiz.views.UserService")
    def test_multiple_correct_answers_invalid(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        data = {
            "question": "Select the correct option.",
            "type": 1,
            "explanation": "Only one should be correct.",
            "answers-TOTAL_FORMS": "2",
            "answers-INITIAL_FORMS": "0",
            "answers-MIN_NUM_FORMS": "0",
            "answers-MAX_NUM_FORMS": "1000",
            "answers-0-text": "Option A",
            "answers-0-is_correct": "on",
            "answers-1-text": "Option B",
            "answers-1-is_correct": "on",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Tylko jedna odpowiedź może być poprawna", html=False
        )
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)

    @patch("quiz.views.UserService")
    def test_invalid_question_type_format(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        data = {
            "question": "What's the capital of France?",
            "type": "not-a-number",
            "explanation": "Should be Paris.",
            "answers-TOTAL_FORMS": "1",
            "answers-INITIAL_FORMS": "0",
            "answers-MIN_NUM_FORMS": "0",
            "answers-MAX_NUM_FORMS": "1000",
            "answers-0-text": "Paris",
            "answers-0-is_correct": "on",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "type", "Wybierz poprawną wartość.")

    @patch("quiz.views.UserService")
    def test_get_context_data_contains_formset(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        response = self.client.get(self.url)
        self.assertIn("formset", response.context)
        self.assertTrue(response.context["formset"].is_valid())

    @patch("quiz.views.AnswerFormSet")
    @patch("quiz.views.UserService")
    def test_form_valid_saves_quiz_and_answers(
        self, mock_user_service, mock_formset_class
    ):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        mock_form = MagicMock()
        mock_quiz = MagicMock()
        mock_form.save.return_value = mock_quiz

        mock_formset = MagicMock()
        mock_formset.is_valid.return_value = True
        mock_formset.save.return_value = None
        mock_formset_class.return_value = mock_formset

        response = QuizCreateView.as_view()(self.client.post(self.url).wsgi_request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

        mock_form.save.assert_called_once()
        mock_formset.save.assert_called_once()


class CategorySelectViewTests(TestCase):
    def setUp(self):
        self.url = reverse("quiz:category_select")
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.form_data = {"category": 1}

    def get_request(self, method="get", data=None, user=None):
        user = user or self.user
        if method == "post":
            request = self.factory.post(self.url, data=data or {})
        else:
            request = self.factory.get(self.url)
        request.user = user

        setattr(request, "session", self.client.session)
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        return request

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("/login/", response.url)

    def test_renders_template_on_get(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quizes/category_select.html")
        self.assertIsInstance(response.context["form"], CategorySelectForm)

    def test_form_valid_redirects_to_quiz_add_with_category(self):
        request = self.get_request(method="post", data=self.form_data)
        response = CategorySelectView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/quiz/add?category_id=1")

    def test_form_invalid_renders_with_errors(self):
        request = self.get_request(method="post", data={})
        response = CategorySelectView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context_data)
        self.assertTrue(response.context_data["form"].errors)
