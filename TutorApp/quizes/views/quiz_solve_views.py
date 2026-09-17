import logging
from datetime import datetime, timedelta
from typing import Any, Dict, OrderedDict
from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic import FormView
from formtools.wizard.views import SessionWizardView

from ..forms.quiz_wizard_forms import QuizStartForm, QuizStepForm
from ..models import SECONDS_PER_QUESTION, Question, Quiz
from ..services.solve_quiz_services import QuizSolveService

logger = logging.getLogger(__name__)


class SolveQuizWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [("dummy", QuizStepForm)]
    template_name = "quizes/quiz_solve_wizard.html"

    def get_form_list(self) -> OrderedDict[str, type]:
        """
        Build dynamic form list based on quiz questions.
        Questions are randomly selected once and saved in the session.
        The time limit is being counted down.

        Returns:
            OrderedDict[str, type]: mapping to [question_id: QuizStepForm]

        Raises:
            ValueError: If the quiz has no questions available (checked directly
                        by this method), or if the underlying call to
                        Quiz.get_random_questions() rejects the requested number of
                        questions (not positive, or exceeding the available pool).
        """

        quiz_pk = self.kwargs["quiz_pk"]
        quiz = get_object_or_404(Quiz, pk=quiz_pk)
        question_ids = self.storage.extra_data.get("question_ids")

        if question_ids is None:

            question_count = self.request.GET.get("question_count", "all")
            get_level_type = self.request.GET.get("level_type")
            try:
                level_type = int(get_level_type)
            except (ValueError, TypeError):
                logger.warning(f"Invalid level_type '{get_level_type}', not using")
                level_type = None

            if question_count == "all":
                count = None
            else:
                try:
                    count = int(question_count)
                except (ValueError, TypeError):
                    logger.warning(
                        f"Invalid question_count '{question_count}', using 10"
                    )
                    count = 10
            questions = quiz.get_random_questions(count, level_type)
            if not questions:
                logger.error(f"Quiz {quiz_pk} has no questions!")
                raise ValueError(f"Quiz '{quiz.title}' has no questions.")

            question_ids = [question.pk for question in questions]
            self.storage.extra_data["question_ids"] = question_ids

            deadline = timezone.now() + timedelta(
                seconds=SECONDS_PER_QUESTION * len(question_ids)
            )
            self.storage.extra_data["deadline"] = deadline.isoformat()
        else:
            questions_qs = Question.objects.filter(id__in=question_ids)

            lookup = {question.pk: question for question in questions_qs}

            questions = [lookup[question_id] for question_id in question_ids]

        dict_with_question_ids = OrderedDict(
            [(f"question_{question.id}", QuizStepForm) for question in questions]
        )
        self.form_list = dict_with_question_ids

        return dict_with_question_ids

    def done(self, form_list: Any, form_dict: Dict, **kwargs) -> HttpResponse:
        """
        Collects and consolidates data on all the questions the user answered
        while taking the quiz, and saves the entire sample,
        the score, and the maximum possible score to the database.

        Args:
            form_list: List required by the framework but unused in this case.
            form_dict: Dict containing all the forms from each step, along with the data entered by the user.

        Returns:
            HttpResponse: A redirect to the quiz summary page for this attempt.

        Raises:
            ValueError: If a question ID doesn't exist (raised by QuizSolveService.calculate_score()).
            ValueError: If a question has no correct answer (raised by QuizSolveService.calculate_question_score()).
            ValueError: If score is negative, max_score is not positive, or score exceeds
            max_score (raised by QuizSolveService.save_quiz_attempt()).
        """

        service = QuizSolveService()
        user = self.request.user

        quiz_pk = self.kwargs["quiz_pk"]
        quiz = get_object_or_404(Quiz, pk=quiz_pk)

        user_answers = []
        for step_name, form_object in form_dict.items():
            selected = form_object.cleaned_data.get("selected_answers", [])
            selected_ids = [int(answer_id) for answer_id in selected]
            user_answers.append((step_name, selected_ids))

        max_score = len(user_answers)

        question_ids = [int(step_name.split("_")[1]) for step_name, _ in user_answers]
        questions = Question.objects.filter(id__in=question_ids)

        score = service.calculate_score(list(questions), user_answers)

        attempt = service.save_quiz_attempt(user, quiz, score, max_score)

        service.save_user_answers(attempt, user_answers)

        return redirect("quizes:quiz_summary", attempt_id=attempt.id)

    def get_context_data(self, form: QuizStepForm, **kwargs: Any) -> Dict[str, Any]:
        """
        Overrides the method then adds the `question` object to the context dictionary and the quiz deadline in string ISO format.

        Args:
            form: Form instance for the current step.

        Returns:
            Dict[str, Any]: Context dictionary with added question object and quiz deadline in string ISO format.

        """
        context = super().get_context_data(form=form, **kwargs)

        current_step = self.steps.current

        question_id = int(current_step.split("_")[1])
        question = get_object_or_404(Question, pk=question_id)
        context["question"] = question
        context["deadline"] = self.storage.extra_data["deadline"]

        return context

    def get_form_kwargs(self, step: str = None) -> Dict[str, Any]:
        """
        Builds and returns a dictionary of arguments passed to the form
        during its initialization for a single step. Adds a Question object to dict on question key.

        Args:
            step: Wizard step id in dict that represents on which step user is,
            if none dict will be empty but in reality it's only
            a defensive safeguard.

        Returns:
            Dict[str, Any]: Dictionary of arguments submitted to form while initializing it with question object.
        """
        if step is None:
            return {}

        kwargs = super().get_form_kwargs(step)
        question_id = int(step.split("_")[1])
        question = get_object_or_404(Question, pk=question_id)
        kwargs["question"] = question
        return kwargs

    def post(self, *args, **kwargs) -> HttpResponse:
        """
        Checks whether the quiz time limit has been exceeded before processing
        the submitted step. If time remains, delegates to the wizard's default
        post() handling. If the deadline has passed, forces the quiz to finish
        via force_finish().

        Returns:
            HttpResponse: The response from the default wizard post() handling
            if time remains, or the redirect returned by force_finish() if the
            deadline has passed.
        """
        deadline = datetime.fromisoformat(self.storage.extra_data["deadline"])

        if deadline > timezone.now():
            return super().post(*args, **kwargs)
        else:
            return self.force_finish()

    def get(self, *args, **kwargs) -> HttpResponse:
        """
        Checks whether the `extra_data` dictionary contains question numbers to determine
        if this is the user's first attempt at the test,
        given that the original `get` method clears the dictionary when called.

        Returns:
            HttpResponse: A rendered form for the quiz question. The specific
            question shown depends on whether this is the first attempt or a
            resumed session.
        """
        if self.storage.extra_data.get("question_ids") is None:
            return super().get(*args, **kwargs)
        else:
            return self.render(self.get_form())

    def force_finish(self) -> HttpResponse:
        """
        Fills in any unanswered wizard steps with empty data, resulting in
        0 points for those questions, then finishes the wizard.

        Returns:
            HttpResponse: A redirect to the quiz summary page for this attempt,
            returned by the wizard's done() method.
        """
        for form_key in self.get_form_list().keys():
            step_data = self.storage.get_step_data(form_key)
            if step_data is None:
                self.storage.set_step_data(form_key, {})

        last_step = self.steps.last

        form = self.get_form(
            step=last_step,
            data=self.storage.get_step_data(last_step),
            files=self.storage.get_step_files(last_step),
        )

        return self.render_done(form)


class QuizStartView(LoginRequiredMixin, FormView):
    model = Quiz
    form_class = QuizStartForm
    template_name = "quizes/quiz_solve_start.html"

    @cached_property
    def quiz(self) -> Quiz:
        """
        Quiz instance resolved from the URL's quiz_pk, cached per request.
        """
        return get_object_or_404(Quiz, pk=self.kwargs["quiz_pk"])

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()

        kwargs["quiz"] = self.quiz
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["quiz"] = self.quiz
        context["question_count"] = self.quiz.questions.count()
        context["seconds_per_question"] = SECONDS_PER_QUESTION
        context["last_attempt"] = self.quiz.get_last_attempt_for_user(self.request.user)

        return context

    def form_valid(self, form: QuizStartForm) -> HttpResponseRedirect:
        question_count = form.cleaned_data["question_count"]
        level_type = form.cleaned_data.get("level_type")

        params = {
            "question_count": question_count,
        }

        if level_type is not None:
            params["level_type"] = level_type
        query_string = urlencode(params)

        base_url = reverse("quizes:solve_quiz", kwargs={"quiz_pk": self.quiz.pk})

        return redirect(f"{base_url}?{query_string}")
