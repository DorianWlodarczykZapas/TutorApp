from typing import Any, Dict, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView
from users.services import UserService

from .forms import AddMatriculationTaskForm, ExamForm
from .models import Exam, MathMatriculationTasks
from .services import MatriculationTaskService


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


class SearchMatriculationTaskView(LoginRequiredMixin, ListView):
    """
    Displays a paginated list of filtered Math Matriculation Tasks with extracted content.
    """

    model = MathMatriculationTasks
    template_name = "tasks/search_tasks.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self) -> list[MathMatriculationTasks]:
        """
        Fetches the filtered queryset based on GET parameters.
        """
        params = self.request.GET

        year = self._get_int_param(params.get("year"))
        month = self._get_int_param(params.get("month"))
        level = self._get_int_param(params.get("level"))
        category = self._get_int_param(params.get("category"))
        is_done = self._get_bool_param(params.get("is_done"))

        return MatriculationTaskService.filter_tasks(
            year=year,
            month=month,
            level=level,
            category=category,
            is_done=is_done,
            user=self.request.user,
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds search parameters and extracted task content to context.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "Search Tasks"
        context["filter"] = self.request.GET

        context["task_contents"] = {
            task.id: MatriculationTaskService.extract_task_content(task)
            for task in context["tasks"]
        }

        return context

    def _get_int_param(self, value: Optional[str]) -> Optional[int]:
        try:
            return int(value) if value else None
        except ValueError:
            return None

    def _get_bool_param(self, value: Optional[str]) -> Optional[bool]:
        if value == "true":
            return True
        elif value == "false":
            return False
        return None
