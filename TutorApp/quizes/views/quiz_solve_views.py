import logging
from typing import Any, Dict, OrderedDict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView
from formtools.wizard.views import SessionWizardView

from ..forms.quiz_wizard_forms import QuizStartForm, QuizStepForm
from ..models import Answer, Question, Quiz, QuizAttempt, UserAnswer

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
        quiz_pk = self.kwargs["quiz_pk"]
        quiz = get_object_or_404(Quiz, pk=quiz_pk)

        user_answers_data = []

        total_score = 0

        max_possible_score = 0

        for step_name in self.get_form_list().keys():
            step_data = self.get_cleaned_data_for_step(step_name)

            selected_answers_ids = step_data.get("selected_answers", [])
            question_id = int(step_name.split("_")[1])
            question = get_object_or_404(Question, pk=question_id)

            all_answers = question.answers.all()

            correct_answers = [a for a in all_answers if a.is_correct]
            correct_count = len(correct_answers)

            points_per_correct = 1.0 / correct_count if correct_count > 0 else 0

            earned_points = 0
            for answer_id in selected_answers_ids:
                answer_id = int(answer_id)

                if any(a.id == answer_id and a.is_correct for a in all_answers):
                    earned_points += points_per_correct

            earned_points = round(earned_points, 2)

            total_score += earned_points

            max_possible_score += 1.0

            user_answers_data.append(
                {
                    "question": question,
                    "selected_answers_ids": [int(aid) for aid in selected_answers_ids],
                    "points_earned": earned_points,
                }
            )

        quiz_attempt = QuizAttempt.objects.create(
            user=self.request.user,
            quiz=quiz,
            score=total_score,
            max_score=int(max_possible_score),
            completed_at=timezone.now(),
        )

        for data in user_answers_data:
            user_answer = UserAnswer.objects.create(
                attempt=quiz_attempt,
                question=data["question"],
                points_earned=data["points_earned"],
            )

            answer_objects = Answer.objects.filter(
                id__in=data["selected_answers_ids"],
            )
            user_answer.selected_answers.set(answer_objects)

        return redirect("quizes:quiz_summary", attempt_id=quiz_attempt.id)

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
