from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.views import TeacherRequiredMixin

from .forms import AnswerFormSet, QuizForm
from .models import Quiz


class QuizCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """
    View for creating a quiz question (Quiz) with a set of answers (Answer).
    It is only available to users with the teacher role
    """

    model = Quiz
    form_class = QuizForm
    template_name = "quiz/add_question_to_quiz.html"
    success_url = reverse_lazy("quiz:add")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds formset to the template context.
        """
        data = super().get_context_data(**kwargs)
        if "formset" not in kwargs:
            data["formset"] = AnswerFormSet()
        data["title"] = _("Add new quiz question")
        return data

    def post(self, request, *args, **kwargs):

        self.object = None
        form = self.get_form()
        formset = AnswerFormSet(self.request.POST, self.request.FILES)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()

        formset.instance = self.object

        formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        context = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(context)
