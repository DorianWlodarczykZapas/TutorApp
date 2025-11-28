from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import FormView
from formtools.wizard.views import SessionWizardView

from ..forms.quiz_wizard_forms import QuizStartForm
from ..models import Quiz


class SolveQuizWizard(LoginRequiredMixin, SessionWizardView):
    template_name = "quizes/quiz_solve_wizard.html"

    def get_form_list(self):
        pass

    def done(self, form_list, **kwargs) -> HttpResponse:
        pass


class QuizStartView(LoginRequiredMixin, FormView):
    model = Quiz
    form_class = QuizStartForm
    template_name = "quizes/quiz_solve_start.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def form_valid(self, form):
        pass
