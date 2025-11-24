from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView
from django_filters.views import FilterView
from users.views import TeacherRequiredMixin

from ..filters import TrainingTaskFilter
from ..forms.training_tasks_forms import TrainingTaskForm
from ..models import TrainingTask


class AddTrainingTask(TeacherRequiredMixin, CreateView):
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


class TrainingTaskListView(LoginRequiredMixin, FilterView):
    """
    ListView for TrainingTask with filtering

    Features:
    - Automatic filtering by user's grade (default)
    - Search by task content
    - Filter by book, section, difficulty level
    - Filter by completion status
    - Pagination
    """

    model = TrainingTask
    filterset_class = TrainingTaskFilter
    template_name = "training_tasks/training_task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def get_filterset_kwargs(self, filterset_class):

        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):

        queryset = super().get_queryset()

        queryset = queryset.select_related("section", "section__book").prefetch_related(
            "completed_by"
        )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["title"] = _("Training Tasks")

        if self.request.user.is_authenticated:
            all_tasks = self.get_queryset()
            context["total_tasks"] = all_tasks.count()
            context["completed_tasks"] = all_tasks.filter(
                completed_by=self.request.user
            ).count()

            if context["total_tasks"] > 0:
                context["completion_percentage"] = round(
                    (context["completed_tasks"] / context["total_tasks"]) * 100
                )
            else:
                context["completion_percentage"] = 0

        return context


class TrainingTaskDetailView(LoginRequiredMixin, DetailView):

    model = TrainingTask
    template_name = "training_tasks/training_task_detail.html"
    context_object_name = "task"

    def get_queryset(self):

        return (
            super()
            .get_queryset()
            .select_related("section", "section__book")
            .prefetch_related("completed_by")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Task Details")

        if self.request.user.is_authenticated:
            context["is_completed"] = self.object.completed_by.filter(
                id=self.request.user.id
            ).exists()

        return context
