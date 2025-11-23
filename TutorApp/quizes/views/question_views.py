from typing import Any, Dict

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView

from ...users.views import TeacherRequiredMixin
from ..forms.question_forms import AnswerFormSet, QuestionForm
from ..models import Question, Quiz


class AddQuestion(TeacherRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = "quizes/add_question.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = AnswerFormSet(self.request.POST)
        else:
            context["formset"] = AnswerFormSet()
        return context

    def form_valid(self, form: QuestionForm) -> HttpResponse:
        formset = AnswerFormSet(self.request.POST)

        if formset.is_valid():
            self.object = form.save(commit=False)
            quiz_pk = self.kwargs["quiz_pk"]
            quiz = Quiz.objects.get(pk=quiz_pk)

            self.object.quiz = quiz
            self.object.save()
            formset.instance = self.object
            formset.save()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self) -> str:
        quiz_pk = self.kwargs["quiz_pk"]
        return reverse_lazy("quizes:add_question", kwargs={"quiz_pk": quiz_pk})
