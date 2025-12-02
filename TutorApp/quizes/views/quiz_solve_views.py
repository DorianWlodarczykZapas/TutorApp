import logging
from typing import Any, Dict, OrderedDict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView
from formtools.wizard.views import SessionWizardView

from ..forms.quiz_wizard_forms import QuizStartForm, QuizStepForm
from ..models import Quiz

logger = logging.getLogger(__name__)


class SolveQuizWizard(LoginRequiredMixin, SessionWizardView):
    template_name = "quizes/quiz_solve_wizard.html"

    def get_form_list(self) -> OrderedDict[str, type]:
        """
        Build dynamic form list based on quiz questions.
        """

        quiz_pk = self.kwargs["quiz_pk"]
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        question_count = self.request.GET.get("question_count", "all")
        questions = quiz.questions.all()

        available_count = questions.count()
        if available_count == 0:
            logger.error(f"Quiz {quiz_pk} has no questions!")
            raise ValueError(f"Quiz '{quiz.title}' has no questions. Cannot start.")

        questions = questions.order_by("?")

        if question_count != "all":
            try:
                question_count = int(question_count)
            except (ValueError, TypeError):
                logger.warning(f"Invalid question_count '{question_count}', using 10")
            question_count = 10

        question_count = min(question_count, available_count)
        questions = questions[:question_count]

        form_list = []
        for question in questions:
            form_list.append((f"question_{question.id}", QuizStepForm))

        return OrderedDict(form_list)

    # def done(self, form_list, **kwargs) -> HttpResponse:
    #     quiz_pk = self.kwargs["quiz_pk"]
    #     quiz = get_object_or_404(Quiz, pk=quiz_pk)
    #
    #     user_answers_data = []
    #
    #     total_score = 0
    #
    #     max_possible_score = 0
    #
    #     for step_name in self.get_form_list().keys():
    #         step_data = self.get_cleaned_data_for_step(step_name)
    #
    #         selected_answers_ids = step_data.get["selected_answers", []]
    #         question_id = int(step_name.split("_")[1])
    #         question = get_object_or_404(Question, pk=question_id)
    #
    #     return redirect('quizes:quiz_list')


class QuizStartView(LoginRequiredMixin, FormView):
    model = Quiz
    form_class = QuizStartForm
    template_name = "quizes/quiz_solve_start.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        quiz_pk = self.kwargs["quiz_pk"]
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        context["quiz"] = quiz
        context["question_count"] = quiz.questions.count()

        return context

    def form_valid(self, form: QuizStartForm) -> HttpResponseRedirect:
        question_count = form.cleaned_data["question_count"]

        quiz_pk = self.kwargs["quiz_pk"]
        return redirect(
            reverse("quizes:solve_quiz", kwargs={"quiz_pk": quiz_pk})
            + f"?question_count={question_count}"
        )
