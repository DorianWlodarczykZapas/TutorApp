from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from ...users.views import TeacherRequiredMixin
from ..forms import AddExamTaskForm
from ..models import ExamTask
from ..services.ExtractTaskContentFromLines import ExtractTaskContentFromLines
from ..services.ExtractTaskTextFromPdf import ExtractTaskTextFromPdf


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
