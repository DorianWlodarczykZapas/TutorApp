import os
from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import Http404, HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import CreateView, DetailView, ListView, View
from django_filters.views import FilterView
from users.views import TeacherRequiredMixin

from ..filters import SCHOOL_TO_EXAM_TYPE, ExamTaskFilter
from ..forms import AddExamTaskForm
from ..models import Exam, ExamTask, Topic
from ..services.examTaskDBService import ExamTaskDBService
from ..services.extractTaskFromPdf import ExtractTaskFromPdf

LEVEL_MAP = {
    "B": 1,
    "E": 2,
}


class AddExamTask(TeacherRequiredMixin, CreateView):
    model = ExamTask
    form_class = AddExamTaskForm
    template_name = "examination_tasks/add_exam_task.html"
    success_url = reverse_lazy("examination_tasks:add_exam_task")

    def form_valid(self, form):
        exam = form.cleaned_data.get("exam")
        task_id = form.cleaned_data.get("task_id")
        pages = form.cleaned_data.get("task_pages", "")

        if exam and exam.exam_file and pages and task_id:
            try:

                page_number = int(pages.split("-")[0]) if "-" in pages else int(pages)

                exam_file_path = exam.exam_file.path

                output_dir = os.path.join(
                    settings.MEDIA_ROOT,
                    "exam_tasks",
                    str(exam.subject.name),
                    str(exam.exam_type),
                    str(exam.year),
                    str(exam.month),
                )

                os.makedirs(output_dir, exist_ok=True)

                extracted_pdf_path = ExtractTaskFromPdf.extract_task(
                    file_path=exam_file_path,
                    task_number=task_id,
                    page_number=page_number,
                    output_dir=output_dir,
                )

                relative_path = os.path.relpath(extracted_pdf_path, settings.MEDIA_ROOT)
                form.instance.task_screen = relative_path

                import pymupdf

                doc = pymupdf.open(extracted_pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                form.instance.task_content = text

            except Exception as e:
                messages.error(
                    self.request, f"Error extracting task from PDF: {str(e)}"
                )
                return self.form_invalid(form)
        elif not exam:
            messages.error(self.request, _("Please select an exam"))
            return self.form_invalid(form)
        elif not exam.exam_file:
            messages.error(self.request, _("Selected exam has no PDF file"))
            return self.form_invalid(form)
        elif not pages:
            messages.warning(
                self.request, _("No page numbers provided - task screen not generated")
            )

        messages.success(self.request, _("Task added successfully!"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = _("Add New Exam Task")
        return ctx


class AjaxTopicsView(View):
    """Returns list of topics for a given section (used for dynamic dropdown)."""

    def get(self, request, *args, **kwargs):
        section_id = request.GET.get("section_id")
        topics = Topic.objects.filter(section_id=section_id).order_by("name")
        data = [{"id": t.id, "name": t.name} for t in topics]
        return JsonResponse(data, safe=False)


class AjaxPreviewTaskView(View):
    def post(self, request, *args, **kwargs):
        try:
            exam_id = request.POST.get("exam_id")
            page_number = int(request.POST.get("page", "1"))
            task_number = int(request.POST.get("task_number", "1"))

            exam = Exam.objects.get(pk=exam_id)

            if not exam.exam_file:
                return JsonResponse({"error": "Exam file not found"}, status=400)

            pdf_path = exam.exam_file.path

            temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_previews")
            os.makedirs(temp_dir, exist_ok=True)

            extracted_pdf_path = ExtractTaskFromPdf.extract_task(
                file_path=pdf_path,
                task_number=task_number,
                page_number=page_number,
                output_dir=temp_dir,
            )

            import pymupdf

            doc = pymupdf.open(extracted_pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            pdf_url = os.path.join(
                settings.MEDIA_URL,
                os.path.relpath(extracted_pdf_path, settings.MEDIA_ROOT),
            )

            return JsonResponse(
                {
                    "pdf_url": pdf_url,
                    "task_text": text[:500] + "..." if len(text) > 500 else text,
                }
            )

        except Exam.DoesNotExist:
            return JsonResponse({"error": "Exam not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class TaskPdfView(LoginRequiredMixin, View):
    template_name = "examination_tasks/exam_task_preview.html"

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
    template_name = "examination_tasks/exam_task_preview.html"
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


class ExamTaskSearchEngine(LoginRequiredMixin, FilterView):
    model = ExamTask
    filterset_class = ExamTaskFilter
    template_name = "examination_tasks/exam_task_search_engine.html"
    paginate_by = 20

    def get_queryset(self) -> QuerySet["ExamTask"]:
        qs = ExamTask.objects.select_related("exam").select_related("section", "topic")
        user = getattr(self.request, "user", None)
        school_type = getattr(user, "school_type", None)

        exam_type = SCHOOL_TO_EXAM_TYPE.get(school_type)
        if exam_type is not None:
            qs = qs.filter(exam__exam_type=exam_type)

        return qs.order_by("-exam__year", "-exam__month", "-id")
