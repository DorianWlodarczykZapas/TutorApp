from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q, QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView
from users.views import TeacherRequiredMixin

from ..forms import ExamForm
from ..models import Exam
from ..services.examTaskDBService import ExamTaskDBService


class AddExam(TeacherRequiredMixin, CreateView):
    """
    View for adding new matriculation exams.
    Access is restricted to logged-in users with teacher privileges.
    """

    model = Exam
    form_class = ExamForm
    template_name = "examination_tasks/add_exam.html"
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


class ExamListView(LoginRequiredMixin, ListView):
    """
    Displays a list of all available exams, enriching them with the user's
    completion status fetched from the ExamService.
    """

    model = Exam
    template_name = "examination_tasks/exam_list.html"
    context_object_name = "exams"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Exam]:
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
