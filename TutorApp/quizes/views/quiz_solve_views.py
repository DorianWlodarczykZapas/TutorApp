from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        quiz_pk = self.kwargs["quiz_pk"]
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        context["quiz"] = quiz

        return context

    def form_valid(self, form: QuizStartForm) -> HttpResponseRedirect:
        question_count = form.cleaned_data["question_count"]

        quiz_pk = self.kwargs["quiz_pk"]
        return redirect(
            reverse("quizes:solve_quiz", kwargs={"quiz_pk": quiz_pk})
            + f"?question_count={question_count}"
        )
