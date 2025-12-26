from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView
from users.views import TeacherRequiredMixin

from ..forms.quiz_forms import QuizForm
from ..models import Quiz


class AddQuiz(TeacherRequiredMixin, CreateView):

    model = Quiz
    form_class = QuizForm
    template_name = "quizes/add_quiz.html"
    success_url = reverse_lazy("quizes:quiz_list")

    def form_valid(self, form: QuizForm) -> HttpResponseRedirect:
        messages.success(self.request, _("Quiz created successfully!"))
        return super().form_valid(form)


class QuizList(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quizes/quiz_list.html"
    context_object_name = "quiz_list"

    def get_queryset(self) -> QuerySet[Quiz]:
        return Quiz.objects.select_related("quizzes").annotate(
            number_of_questions=Count("questions")
        )
