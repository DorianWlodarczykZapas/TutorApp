from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from ...users.views import TeacherRequiredMixin
from ..forms.quiz_forms import QuizForm
from ..models import Quiz


class AddQuiz(TeacherRequiredMixin, CreateView):

    model = Quiz
    form_class = QuizForm
    template_name = "quizes/add_quiz.html"
    success_url = reverse_lazy("quizes:quiz_list")


class QuizList(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quizes/quiz_list.html"
    context_object_name = "quiz_list"
