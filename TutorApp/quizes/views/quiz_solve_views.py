import logging
from typing import Any, Dict, OrderedDict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView
from formtools.wizard.views import SessionWizardView

from ..forms.quiz_wizard_forms import QuizStartForm, QuizStepForm
from ..models import Question, Quiz
from ..services.solve_quiz_services import QuizSolveService

logger = logging.getLogger(__name__)


class SolveQuizWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [("dummy", QuizStepForm)]
    template_name = "quizes/quiz_solve_wizard.html"

    def get_form_list(self) -> OrderedDict[str, type]:
        """
        Build dynamic form list based on quiz questions.
        """

        quiz_pk = self.kwargs["quiz_pk"]
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        question_count = self.request.GET.get("question_count", "all")

        if question_count == "all":
            questions = quiz.questions.all().order_by("?")
        else:
            try:
                count = int(question_count)
            except (ValueError, TypeError):
                logger.warning(f"Invalid question_count '{question_count}', using 10")
                count = 10
            questions = quiz.get_random_questions(count)

        if not questions:
            logger.error(f"Quiz {quiz_pk} has no questions!")
            raise ValueError(f"Quiz '{quiz.title}' has no questions.")

        form_list = [
            (f"question_{question.id}", QuizStepForm) for question in questions
        ]

        return OrderedDict(form_list)

    def done(self, form_list, **kwargs) -> HttpResponse:

        service = QuizSolveService()
        user = self.request.user

        quiz_pk = self.kwargs["quiz_pk"]
        quiz = get_object_or_404(Quiz, pk=quiz_pk)

        user_answers = []
        for step_name in self.get_form_list().keys():
            selected = self.get_cleaned_data_for_step(step_name).get(
                "selected_answers", []
            )
            selected_ids = [int(id) for id in selected]
            user_answers.append((step_name, selected_ids))

        max_score = len(user_answers)

        question_ids = [int(step_name.split("_")[1]) for step_name, _ in user_answers]
        questions = Question.objects.filter(id__in=question_ids)

        score = service.calculate_score(list(questions), user_answers)

        attempt = service.save_quiz_attempt(user, quiz, score, max_score)

        service.save_user_answers(attempt, user_answers)

        return redirect("quizes:quiz_summary", attempt_id=attempt.id)

    def get_context_data(self, form: QuizStepForm, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(form=form, **kwargs)

        current_step = self.steps.current

        question_id = int(current_step.split("_")[1])
        question = get_object_or_404(Question, pk=question_id)
        context["question"] = question
        return context


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
