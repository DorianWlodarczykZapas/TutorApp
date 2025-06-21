from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.services import UserService

from .forms import AnswerFormSet, QuizForm
from .models import Quiz


class QuizCreateView(LoginRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quiz/quiz_form.html"
    success_url = reverse_lazy("quiz:add")

    def dispatch(self, request, *args, **kwargs):
        if not UserService(request.user).is_teacher():
            raise PermissionDenied(_("You do not have permission to access this page."))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = AnswerFormSet(self.request.POST)
        else:
            context["formset"] = AnswerFormSet()
        context["title"] = _("Add new quiz question")
        return context

    def form_valid(self, form: QuizForm):
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form: QuizForm):
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context)
