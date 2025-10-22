from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.views import TeacherRequiredMixin

from ..forms import TrainingTaskForm
from ..models import TrainingTask


class AddTrainingTask(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """
    View that allows teachers to add new training tasks (optionally linked to book sections).
    """

    model = TrainingTask
    form_class = TrainingTaskForm
    template_name = "examination_tasks/add_training_task.html"
    success_url = reverse_lazy("examination_tasks:add_training_task")

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["title"] = _("Add New Training Task")
        return data

    def form_valid(self, form: TrainingTaskForm) -> HttpResponseRedirect:
        messages.success(self.request, _("Training task added successfully!"))
        return super().form_valid(form)
