from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import CreateView, DetailView, ListView, View
from formtools.wizard.views import SessionWizardView
from users.views import TeacherRequiredMixin

from .forms import AddMatriculationTaskForm, BookForm, ConfirmTaskContentForm, ExamForm
from .models import Book, Exam, ExamTask
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


FORMS = [
    ("step1", AddMatriculationTaskForm),
    ("step2", ConfirmTaskContentForm),
]


class AddMatriculationTaskWizard(
    LoginRequiredMixin, TeacherRequiredMixin, SessionWizardView
):
    template_name = "examination_tasks/task_wizard.html"
    form_list = FORMS

    def get_form_instance(self, step):
        if step == "step2":
            instance = ExamTask()
            step1_data = self.get_cleaned_data_for_step("step1") or {}
            for field, value in step1_data.items():
                setattr(instance, field, value)

            exam = step1_data.get("exam")
            task_id = step1_data.get("task_id")
            pages_str = step1_data.get("task_pages")
            pages = MatriculationTaskService._parse_pages_string(pages_str)

            extracted_text = MatriculationTaskService.extract_text_lines_from_pdf(
                exam.tasks_link.path, pages
            )

            task_content = MatriculationTaskService.get_clean_task_content(
                extracted_text, task_id
            )
            instance.task_content = task_content

            return instance
        return None

    def done(self, form_list, **kwargs):
        step1_data = self.get_cleaned_data_for_step("step1")
        step2_data = self.get_cleaned_data_for_step("step2")

        exam_task = ExamTask(
            exam=step1_data["exam"],
            task_id=step1_data["task_id"],
            section=step1_data["section"],
            task_pages=step1_data.get("task_pages"),
            answer_pages=step1_data.get("answer_pages"),
            task_content=step2_data["task_content"],
        )
        exam_task.save()

        messages.success(self.request, _("Task added successfully!"))
        return redirect("examination_tasks:add_exam_task")

    def get_success_url(self) -> str:
        """
               Returns the URL to which the user will be redirected on success.
               In this case, we want the page to simply refresh,
        which allows another task to be added to the same exam.
        """
        messages.success(self.request, _("Task added successfully!"))
        return self.request.path_info


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

    model = ExamTask
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
        task = get_object_or_404(ExamTask, pk=task_pk)

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

        task_completion_map = MatriculationTaskService.get_task_completion_map(
            user=self.request.user, exam=self.exam
        )

        for task in context["tasks"]:

            task.is_completed_by_user = task_completion_map.get(task.task_id, False)

        return context


class AddBookView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """
    Simple view that adds book to database via form
    """

    model = Book
    form_class = BookForm
    template_name = "examination_tasks/add_book.html"
    success_url = reverse_lazy("examination_tasks:add_book")

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds the page title to the template context.
        """
        data = super().get_context_data(**kwargs)
        data["title"] = _("Add New Book")
        return data

    def form_valid(self, form: BookForm) -> HttpResponseRedirect:
        """
        Method for handling the form for adding examinations to the database
        """
        messages.success(self.request, _("Book added successfully!"))
        return super().form_valid(form)
