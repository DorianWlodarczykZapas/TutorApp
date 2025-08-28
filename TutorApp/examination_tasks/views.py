from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.db.models.query import QuerySet
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
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
    template_name = "examination_tasks/add_matriculation_task.html"

    def form_valid(self, form):

        task_link = form.cleaned_data.get("task_link")
        pages = form.cleaned_data.get("pages")
        task_id = form.cleaned_data.get("task_id")

        extracted_text = MatriculationTaskService.extract_text_lines_from_pdf(
            task_link, pages
        )
        task_text = MatriculationTaskService.get_clean_task_content(
            extracted_text, task_id
        )

        if task_text:
            form.instance.task_text = task_text
        else:
            messages.warning(self.request, _("Unable to extract text from PDF."))

        return super().form_valid(form)

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
    template_name = "examination_tasks/exam_preview.html"

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
    template_name = "examination_tasks/exam_preview.html"
    context_object_name = "task"

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        status = MatriculationTaskService.toggle_completed(task, request.user)

        return JsonResponse({"completed": status})


@method_decorator(xframe_options_sameorigin, name="dispatch")
class TaskPdfStreamView(View):
    """
     A view that generates and streams raw PDF data for a single, specific task.
    This view is intended to be called by the <embed> or <object> tag on an HTML page.
    It supports GET requests on URLs of the form /examination_tasks/<int:pk>/pdf-stream/.
    """

    def get(self, request, *args, **kwargs):
        task_pk = self.kwargs.get("pk")
        task = get_object_or_404(MathMatriculationTasks, pk=task_pk)

        source_pdf_path = task.exam.tasks_link.path
        pages_str = task.pages

        if not source_pdf_path:
            return HttpResponseNotFound(_("No defined path to the PDF sheet."))

        try:
            pages_to_extract = MatriculationTaskService._parse_pages_string(pages_str)
            if not pages_to_extract:
                return HttpResponseNotFound(
                    _("No pages to be cut have been defined for this task.")
                )

            pdf_bytes = MatriculationTaskService.get_single_task_pdf(
                task_link=source_pdf_path, pages=pages_to_extract
            )

            if not pdf_bytes:
                return HttpResponseNotFound(
                    _("The PDF file for this task could not be generated.")
                )

            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'inline; filename="zadanie_{task.exam.year}_{task.task_id}.pdf"'
            )
            return response

        except Exception:
            return HttpResponse(
                _("An internal server error has occurred. "), status=500
            )


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

        completion_map = MatriculationTaskService.get_user_completion_map_for_exams(
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

    model = MathMatriculationTasks
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

        task_completion_map = MatriculationTaskService.get_task_completion_map(
            user=self.request.user, exam=self.exam
        )

        for task in context["tasks"]:

            task.is_completed_by_user = task_completion_map.get(task.task_id, False)

        return context
