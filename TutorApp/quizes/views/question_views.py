from typing import Any, Dict

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django_stubs_ext import StrOrPromise
from users.views import TeacherRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
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
            quiz = get_object_or_404(Quiz, pk=quiz_pk)

            self.object.quiz = quiz
            self.object.save()
            formset.instance = self.object
            formset.save()

             messages.success(self.request, _("Question has been successfully added."))

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self) -> StrOrPromise:
        quiz_pk = self.kwargs["quiz_pk"]
        return reverse_lazy("quizes:add_question", kwargs={"quiz_pk": quiz_pk})
