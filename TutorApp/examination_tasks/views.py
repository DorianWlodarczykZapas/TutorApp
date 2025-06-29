from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.services import UserService

from .forms import AddMatriculationTaskForm, ExamForm
from .models import Exam, MathMatriculationTasks


class ExamCreateView(LoginRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "examination_tasks/exam_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role_type != 2:
            return HttpResponseForbidden(
                _("You do not have permission to access this page.")
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["title"] = _("Add New Exam")
        return data

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Exam added successfully!"))
        return HttpResponseRedirect(reverse_lazy("examination_tasks:exam_add"))


class AddMatriculationTaskView(LoginRequiredMixin, CreateView):
    model = MathMatriculationTasks
    form_class = AddMatriculationTaskForm
    template_name = "tasks/add_matriculation_task.html"

    def dispatch(self, request, *args, **kwargs):
        user_service = UserService(request.user)
        if not user_service.is_teacher():
            raise PermissionDenied(_("Only teachers can add exam tasks."))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponseRedirect(self.request.path_info)
