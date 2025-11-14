import logging
import os
import shutil
from typing import Any, Dict

import pymupdf
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.db.models import QuerySet
from django.forms import Form
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseNotFound,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import DetailView, ListView, View
from django_filters.views import FilterView
from formtools.wizard.views import SessionWizardView
from users.views import TeacherRequiredMixin

from ..filters import SCHOOL_TO_EXAM_TYPE, ExamTaskFilter
from ..forms import ExamTaskBasicForm, ExamTaskPreviewForm
from ..models import Exam, ExamTask
from ..services.examTaskDBService import ExamTaskDBService
from ..services.extractTaskFromPdf import ExtractTaskFromPdf

LEVEL_MAP = {
    "B": 1,
    "E": 2,
}
logger = logging.getLogger(__name__)


class AddExamTaskWizard(TeacherRequiredMixin, SessionWizardView):
    """
    Wizard for adding exam tasks in 2 steps:

    Step 1 (basic_data): Collecting form data (exam, task_id, pages, etc.)
    Step 2 (preview): Showing PDF and text preview before saving

    User can:
    - Cancel at any step (cleans temp files)
    - Go back to edit (keeps temp files)
    - Save task (moves temp PDF to final location)
    """

    STEP_BASIC = "basic_data"
    STEP_PREVIEW = "preview"

    form_list = [
        (STEP_BASIC, ExamTaskBasicForm),
        (STEP_PREVIEW, ExamTaskPreviewForm),
    ]

    template_name = "examination_tasks/add_exam_task.html"

    file_storage = FileSystemStorage(location=settings.TEMP_WIZARD_DIR)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "cancel" in request.GET:
            return self.cancel()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, form: Form, **kwargs: Any) -> Dict[str, Any]:

        context = super().get_context_data(form, **kwargs)
        context["title"] = _("Add New Exam Task")

        if self.steps.current == self.STEP_PREVIEW:
            context.update(self._generate_preview_context())

        return context

    def get_form_initial(self, step: str) -> Dict[str, Any]:
        """
        Sets initial values for forms

        """
        initial = super().get_form_initial(step)

        if step == self.STEP_PREVIEW:

            initial.update(
                {
                    "task_content": self.storage.extra_data.get("task_content", ""),
                    "task_screen": self.storage.extra_data.get("task_screen", ""),
                }
            )

        return initial

    def _generate_preview_context(self) -> Dict[str, Any]:
        """
        Generates pdf and task content only once

        Returns:
            Dictionary data to show in template
        """
        basic_data = self.get_cleaned_data_for_step(self.STEP_BASIC)

        if not basic_data:
            return {}

        exam = basic_data["exam"]
        task_id = basic_data["task_id"]
        task_pages = basic_data["task_pages"]

        try:

            page_number = (
                int(task_pages.split("-")[0]) if "-" in task_pages else int(task_pages)
            )
        except ValueError:
            messages.error(self.request, _("Invalid page number format."))
            return {"preview_error": _("Invalid page number format.")}

        exam_file_path = exam.exam_file.path

        temp_output_dir = settings.TEMP_WIZARD_DIR
        os.makedirs(temp_output_dir, exist_ok=True)

        try:
            extracted_pdf_path = ExtractTaskFromPdf.extract_task(
                file_path=exam_file_path,
                task_number=task_id,
                page_number=page_number,
                output_dir=temp_output_dir,
            )
        except FileNotFoundError:
            messages.error(self.request, _("Exam file not found."))
            return {"preview_error": "Exam file not found"}
        except Exception:
            logger.exception("Unexpected error while extracting PDF task")
            messages.error(self.request, _("Unexpected PDF extraction error."))
            return {"preview_error": "Unexpected error extracting PDF"}

        try:
            doc = pymupdf.open(extracted_pdf_path)
            text = "".join(page.get_text() for page in doc)
            doc.close()
        except pymupdf.FitzError:
            logger.error("Could not read generated PDF (fitz error)")
            return {"preview_error": "Error reading extracted PDF"}
        except OSError as e:
            logger.error("OS error reading PDF: %s", e)
            return {"preview_error": "OS error reading extracted PDF"}

        relative_path = os.path.relpath(extracted_pdf_path, settings.MEDIA_ROOT)

        self.storage.extra_data.update(
            {
                "extracted_pdf_path": extracted_pdf_path,
                "task_content": text,
                "task_screen": relative_path,
            }
        )

        return {
            "pdf_preview_url": os.path.join(
                settings.TEMP_WIZARD_DIR, os.path.basename(extracted_pdf_path)
            ),
            "task_text_preview": text[:500] + "..." if len(text) > 500 else text,
            "task_screen_path": relative_path,
        }

    def cancel(self) -> HttpResponse:
        """Cancels wizard and cleans temp files."""
        self._cleanup_temp_files()
        self.storage.reset()
        messages.info(self.request, _("Task creation cancelled. No data was saved."))
        return redirect("examination_tasks:add_exam_task")

    @transaction.atomic
    def done(self, form_list, **kwargs):
        """
        Method that uses all previous methods to save to database
        Returns:
            Redirect response
        """

        basic_data = self.get_cleaned_data_for_step("basic_data")
        preview_data = self.get_cleaned_data_for_step("preview")

        exam = basic_data["exam"]
        task_id = basic_data["task_id"]

        try:

            temp_pdf_path = self.storage.extra_data.get("extracted_pdf_path")

            if not temp_pdf_path or not os.path.exists(temp_pdf_path):
                raise FileNotFoundError("Temporary PDF not found")

            final_output_dir = os.path.join(
                settings.MEDIA_ROOT,
                "exam_tasks",
                str(exam.subject.name),
                str(exam.exam_type),
                str(exam.year),
                str(exam.month),
            )
            os.makedirs(final_output_dir, exist_ok=True)

            final_pdf_name = f"zadanie_{task_id}.pdf"
            final_pdf_path = os.path.join(final_output_dir, final_pdf_name)
            shutil.move(temp_pdf_path, final_pdf_path)

            relative_path = os.path.relpath(final_pdf_path, settings.MEDIA_ROOT)

            ExamTask.objects.create(
                exam=exam,
                task_id=task_id,
                section=basic_data.get("section"),
                topic=basic_data.get("topic"),
                task_pages=basic_data["task_pages"],
                answer_pages=basic_data.get("answer_pages", ""),
                task_screen=relative_path,
                task_content=preview_data.get("task_content", ""),
            )

            self._cleanup_temp_files()

            self.storage.reset()

            messages.success(
                self.request,
                _("Task %(task_id)s added successfully!") % {"task_id": task_id},
            )

            return redirect("examination_tasks:add_exam_task")

        except Exception as e:
            messages.error(
                self.request, _("Error saving task: %(error)s") % {"error": str(e)}
            )
            return self.render_revalidation_failure(
                self.steps.current, self.get_form(), **kwargs
            )

    def _cleanup_temp_files(self):
        """
        Deletes all temp files which was created during adding exam task
        """
        temp_dir = settings.TEMP_WIZARD_DIR
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)
            except Exception as e:

                print(f"Warning: Could not clean temp directory: {e}")


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

        if kind == "task":  # STALA TASK
            source_file = exam.tasks_link
            pages_str = task.task_pages
            filename_prefix = "zadanie"
        elif kind == "answer":
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
