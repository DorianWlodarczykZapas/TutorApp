from typing import Any, Dict

from django.http import HttpResponse
from django.views.generic import CreateView

from ...users.views import TeacherRequiredMixin
from ..forms.question_forms import AnswerFormSet, QuestionForm
from ..models import Question


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
        return super().form_valid(form)
