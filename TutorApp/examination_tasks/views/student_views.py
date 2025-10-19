from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django_filters.views import FilterView

from ..filters import SCHOOL_TO_EXAM_TYPE, ExamTaskFilter
from ..models import Exam, ExamTask
from ..services import ExamTaskDBService


class ExamListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all available exams, enriching them with the user's
    completion status fetched from the ExamService.
    """

    model = Exam
    template_name = "examination_tasks/exam_list.html"
    context_object_name = "exams"
    paginate_by = 10

    def get_queryset(self):
        """
        Dynamically filters the queryset based on URL parameters for
        level and user's completion status.
        """

        queryset = super().get_queryset()
        user = self.request.user

        level = self.request.GET.get("level")
        if level in ["1", "2"]:
            queryset = queryset.filter(level_type=level)

        status = self.request.GET.get("status")
        if status in ["not_started", "in_progress", "completed"]:

            user_completed_annotation = Count(
                "tasks", filter=Q(tasks__completed_by=user)
            )
            queryset = queryset.annotate(user_completed_count=user_completed_annotation)

            if status == "not_started":

                queryset = queryset.filter(user_completed_count=0)
            elif status == "in_progress":

                queryset = queryset.filter(
                    user_completed_count__gt=0,
                    user_completed_count__lt=F("tasks_count"),
                )
            elif status == "completed":

                queryset = queryset.filter(user_completed_count=F("tasks_count"))

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds user-specific completion data to each exam object.
        """

        context = super().get_context_data(**kwargs)
        exams_on_page = context["exams"]

        completion_map = ExamTaskDBService.get_user_completion_map_for_exams(
            user=self.request.user, exams=exams_on_page
        )

        for exam in exams_on_page:
            exam.user_completion = completion_map.get(exam.pk, 0)

        context["current_level"] = self.request.GET.get("level")
        context["current_status"] = self.request.GET.get("status")

        context["exams"] = exams_on_page
        return context


class ExamTaskListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all tasks for a specific exam, along with the
    user's completion status for each task.
    """

    model = ExamTask
    template_name = "examination_tasks/exam_task_list.html"
    context_object_name = "tasks"
    paginate_by = 15

    def get_queryset(self):
        """
        Returns the tasks that belong only to the specific exam
        identified by the 'exam_pk' in the URL.
        """
        self.exam = get_object_or_404(Exam, pk=self.kwargs["exam_pk"])

        return self.model.objects.filter(exam=self.exam).order_by("task_id")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds the parent exam object and the task completion map to the context.
        """
        context = super().get_context_data(**kwargs)

        context["exam"] = self.exam

        task_completion_map = ExamTaskDBService.get_task_completion_map(
            user=self.request.user, exam=self.exam
        )

        for task in context["tasks"]:

            task.is_completed_by_user = task_completion_map.get(task.task_id, False)

        return context


class ExamTaskSearchEngine(FilterView):
    model = ExamTask
    filterset_class = ExamTaskFilter
    template_name = "examination_tasks/exam_question_search_engine.html"
    paginate_by = 20

    def get_queryset(self) -> QuerySet["ExamTask"]:
        qs = ExamTask.objects.select_related("exam").select_related("section", "topic")
        user = getattr(self.request, "user", None)
        school_type = getattr(user, "school_type", None)

        exam_type = SCHOOL_TO_EXAM_TYPE.get(school_type)
        if exam_type is not None:
            qs = qs.filter(exam__exam_type=exam_type)

        return qs.order_by("-exam__year", "-exam__month", "-id")
