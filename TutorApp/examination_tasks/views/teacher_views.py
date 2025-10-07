from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.views import TeacherRequiredMixin

from .forms import ExamForm
from .models import Exam


class ExamCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """
    View for adding new matriculation exams.
    Access is restricted to logged-in users with teacher privileges.
    """

    model = Exam
    form_class = ExamForm
    template_name = "examination_tasks/exam_form.html"
    success_url = reverse_lazy("examination_tasks:exam_add")

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds the page title to the template context.
        """
        data = super().get_context_data(**kwargs)
        data["title"] = _("Add New Exam")
        return data

    def form_valid(self, form: ExamForm) -> HttpResponseRedirect:
        """
        Method for handling the form for adding examinations to the database
        """
        messages.success(self.request, _("Exam added successfully!"))
        return super().form_valid(form)
