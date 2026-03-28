from typing import Any, Dict

from courses.filters import TrainingTaskFilter
from courses.forms.training_tasks_forms import TrainingTaskForm
from courses.models import TrainingTask, UserTaskCompletion
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef, QuerySet
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView
from django_filters.views import FilterView
from plans.models import UserPlan
from users.mixins import TeacherRequiredMixin


class AddTrainingTask(TeacherRequiredMixin, CreateView):
    """
    View that allows teachers to add new training tasks (optionally linked to book sections).
    """

    model = TrainingTask
    form_class = TrainingTaskForm
    template_name = "courses/add_training_task.html"
    success_url = reverse_lazy("courses:add_training_task")

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
    - Search by task content, section
    - Filter by level
    - Sort by completed status
    """

    model = TrainingTask
    filterset_class = TrainingTaskFilter
    template_name = "courses/training_task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def get_queryset(self) -> QuerySet[TrainingTask]:
        user = self.request.user
        return (
            TrainingTask.objects.annotate(
                is_completed=Exists(
                    UserTaskCompletion.objects.filter(
                        task=OuterRef("pk"),
                        user=user,
                    )
                )
            )
            .order_by("is_completed")
            .select_related("section")
        )


class TrainingTaskDetailView(LoginRequiredMixin, DetailView):

    model = TrainingTask
    template_name = "courses/training_task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        try:
            is_premium = self.request.user.userplan.is_premium_or_trial
        except UserPlan.DoesNotExist:
            is_premium = False

        context["is_premium"] = is_premium

        if self.object.explanation_timestamp:
            context["video_id"] = (
                self.object.explanation_timestamp.video.youtube_video_id
            )
            context["start_seconds"] = self.object.explanation_timestamp.start_seconds
            context["end_seconds"] = (
                self.object.explanation_timestamp.next_start_seconds
            )

        context["is_completed"] = UserTaskCompletion.objects.filter(
            user=self.request.user, task=self.object
        ).exists()

        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        self.object = self.get_object()

        obj, created = UserTaskCompletion.objects.update_or_create(
            user=request.user,
            task=self.object,
            defaults={"completed_at": timezone.now()},
        )

        return JsonResponse(
            {
                "status": "success",
                "message": _("Task marked as completed!"),
                "is_created": created,
            }
        )
