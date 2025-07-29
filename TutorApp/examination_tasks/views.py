from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View
from users.views import TeacherRequiredMixin

from .forms import AddMatriculationTaskForm, ExamForm, TaskSearchForm
from .models import Exam, MathMatriculationTasks
from .services import MatriculationTaskService


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


class AddMatriculationTaskView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """
    View for adding individual maths tasks to an existing exam.
    Access is restricted to logged-in users with teacher privileges.
    """

    model = MathMatriculationTasks
    form_class = AddMatriculationTaskForm
    template_name = "tasks/add_matriculation_task.html"

    def get_success_url(self) -> str:
        """
               Returns the URL to which the user will be redirected on success.
               In this case, we want the page to simply refresh,
        which allows another task to be added to the same exam.
        """
        messages.success(self.request, _("Task added successfully!"))
        return self.request.path_info


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
            return self.model.objects.none()

        return MatriculationTaskService.filter_tasks(
            user=self.request.user, **form.cleaned_data
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds a filter form to the template context,
        so that it can be displayed and filter values can be stored.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "Search Tasks"
        context["filter_form"] = TaskSearchForm(self.request.GET or None)

        return context


class ExamProgressView(LoginRequiredMixin, TemplateView):
    template_name = "exam_progress.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")
        level = self.request.GET.get("level")

        exams = Exam.objects.all()

        if year:
            exams = exams.filter(year=year)
            context["available_months"] = exams.values_list(
                "month", flat=True
            ).distinct()
        if year and month:
            context["available_levels"] = (
                exams.filter(month=month)
                .values_list("level_type", flat=True)
                .distinct()
            )

        tasks = []
        selected_exam = None
        if year and month and level:
            selected_exam = get_object_or_404(
                Exam, year=year, month=month, level_type=level
            )
            tasks = MathMatriculationTasks.objects.filter(exam=selected_exam).order_by(
                "task_id"
            )

        context.update(
            {
                "years": Exam.objects.values_list("year", flat=True).distinct(),
                "selected_year": year,
                "selected_month": month,
                "selected_level": level,
                "tasks": tasks,
                "selected_exam": selected_exam,
            }
        )
        return context


LEVEL_MAP = {
    "B": 1,
    "E": 2,
}


class TaskPdfView(View):
    template_name = "exam_preview.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        level_str = kwargs.get("level")
        year = kwargs.get("year")
        month = kwargs.get("month")
        task_id = kwargs.get("task_id")

        if level_str not in LEVEL_MAP:
            raise Http404(_("Invalid level"))

        level_type = LEVEL_MAP[level_str]

        try:
            exam = Exam.objects.get(level_type=level_type, year=year, month=month)
        except Exam.DoesNotExist:
            raise Http404(_("Exam not found"))

        context["tasks_link"] = exam.tasks_link
        context["task_id"] = task_id
        return context


class TaskDisplayView(DetailView):
    """
    A view that renders an HTML page with a navbar,
    embedding a PDF for a specific task.
    """

    model = MathMatriculationTasks
    template_name = "exam_preview.html"
    context_object_name = "task"
