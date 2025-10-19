from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import Http404, HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import CreateView, DetailView, ListView, View
from django_filters.views import FilterView

from ...users.views import TeacherRequiredMixin
from ..filters import SCHOOL_TO_EXAM_TYPE, ExamTaskFilter
from ..forms import AddExamTaskForm
from ..models import Exam, ExamTask
from ..services.ExamTaskDBService import ExamTaskDBService
from ..services.ExtractTaskContentFromLines import ExtractTaskContentFromLines
from ..services.ExtractTaskFromPdf import ExtractTaskFromPdf
from ..services.ExtractTaskTextFromPdf import ExtractTaskTextFromPdf

LEVEL_MAP = {
    "B": 1,
    "E": 2,
}


class AddExamTask(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """
    View for adding individual maths tasks to an existing exam.
    Access is restricted to logged-in users with teacher privileges.
    """

    model = ExamTask
    form_class = AddExamTaskForm
    template_name = "examination_tasks/add_matriculation_task.html"

    def form_valid(self, form):

        task_link = form.cleaned_data.get("task_link")
        pages = form.cleaned_data.get("pages")
        task_id = form.cleaned_data.get("task_id")

        extracted_text = ExtractTaskTextFromPdf.extract_text_lines_from_pdf(
            task_link, pages
        )
        task_text = ExtractTaskContentFromLines.get_clean_task_content(
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


class TaskPdfView(LoginRequiredMixin, View):
    template_name = "examination_tasks/task_preview.html"

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


class TaskDisplayView(LoginRequiredMixin, DetailView):
    """
    A view that renders an HTML page with a navbar,
    embedding a PDF for a specific task.
    """

    model = ExamTask
    template_name = "examination_tasks/task_preview.html"
    context_object_name = "task"

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        status = ExamTaskDBService.toggle_completed(task, request.user)

        return JsonResponse({"completed": status})


@method_decorator(xframe_options_sameorigin, name="dispatch")
class TaskCutPdfStreamView(LoginRequiredMixin, View):
    """
    Streams a cut PDF for either the task content ('task') or the solution ('answer').
    """

    VALID_KINDS = ("task", "answer")

    def get(self, request, *args, **kwargs):
        task_pk = kwargs.get("pk")
        kind = kwargs.get("kind", "task")
        if kind not in self.VALID_KINDS:
            return HttpResponseNotFound(_("Incorrect PDF source type."))

        task = get_object_or_404(ExamTask, pk=task_pk)
        exam = task.exam

        if kind == "task":
            source_file = exam.tasks_link
            pages_str = task.task_pages
            filename_prefix = "zadanie"
        else:
            source_file = exam.solutions_link
            pages_str = task.answer_pages
            filename_prefix = "rozwiazanie"

        if not source_file:
            return HttpResponseNotFound(
                _("No PDF file for the selected type: %(kind)s") % {"kind": kind}
            )

        try:
            source_pdf_path = source_file.path
        except Exception:
            return HttpResponseNotFound(_("Unable to read the path to the PDF."))

        try:
            pages_to_extract = ExamTaskDBService._parse_pages_string(pages_str)
            if not pages_to_extract:
                return HttpResponseNotFound(_("Pages to be cut have not been defined."))

            pdf_bytes = ExtractTaskFromPdf.get_single_task_pdf(
                task_link=source_pdf_path, pages=pages_to_extract
            )
            if not pdf_bytes:
                return HttpResponseNotFound(_("Unable to generate PDF file."))

            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'inline; filename="{filename_prefix}_{task.exam.year}_{task.task_id}.pdf"'
            )
            response["Content-Length"] = str(len(pdf_bytes))
            return response

        except Exception:

            return HttpResponse(_("An internal server error has occurred."), status=500)


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
