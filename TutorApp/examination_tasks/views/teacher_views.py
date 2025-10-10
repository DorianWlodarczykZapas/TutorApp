from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.views import TeacherRequiredMixin

from .forms import AddMatriculationTaskForm, BookForm, ExamForm
from .models import Book, Exam, ExamTask
from .services import MatriculationTaskService


class AddExam(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
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


class AddExamTask(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    """
    View for adding individual maths tasks to an existing exam.
    Access is restricted to logged-in users with teacher privileges.
    """

    model = ExamTask
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


class AddBook(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
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
