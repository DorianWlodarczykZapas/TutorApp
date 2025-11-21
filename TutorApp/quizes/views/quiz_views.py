from django.urls import reverse_lazy
from django.views.generic import CreateView

from ...users.views import TeacherRequiredMixin
from ..forms.quiz_forms import QuizForm
from ..models import Quiz


class AddQuiz(TeacherRequiredMixin, CreateView):

    model = Quiz
    form_class = QuizForm
    template_name = "quizes/add_quiz.html"
    success_url = reverse_lazy("quizes:quiz_list")
