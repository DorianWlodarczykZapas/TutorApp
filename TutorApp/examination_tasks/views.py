from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView
from users.views import TeacherRequiredMixin

from .forms import AddMatriculationTaskForm, ExamForm, TaskSearchForm
from .models import Exam, MathMatriculationTasks
from .services import MatriculationTaskService


class ExamCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "examination_tasks/exam_form.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["title"] = _("Add New Exam")
        return data

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Exam added successfully!"))
        return HttpResponseRedirect(reverse_lazy("examination_tasks:exam_add"))


class AddMatriculationTaskView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = MathMatriculationTasks
    form_class = AddMatriculationTaskForm
    template_name = "tasks/add_matriculation_task.html"

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponseRedirect(self.request.path_info)


class SearchMatriculationTaskView(LoginRequiredMixin, ListView):
    """
    Displays a paginated list of filtered Math Matriculation Tasks.
    Filtering logic is handled by a Django form.
    """

    model = MathMatriculationTasks
    template_name = "tasks/search_tasks.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[MathMatriculationTasks]:
        """
        Fetches the filtered queryset based on form-validated GET parameters.
        """

        form = TaskSearchForm(self.request.GET)

        if not form.is_valid():
            return MathMatriculationTasks.objects.none()

        return MatriculationTaskService.filter_tasks(
            user=self.request.user, **form.cleaned_data
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["title"] = "Search Tasks"
        context["filter_form"] = TaskSearchForm(self.request.GET or None)

        return context
