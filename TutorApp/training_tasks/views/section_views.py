from typing import Any, Dict

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.mixins import TeacherRequiredMixin

from TutorApp.examination_tasks.forms.section_forms import SectionForm
from TutorApp.examination_tasks.models import Section


class AddSection(TeacherRequiredMixin, CreateView):
    """
    Simple view that adds section to database via form
    """

    model = Section
    form = SectionForm
    template_name = "examination_tasks/add_section.html"
    success_url = reverse_lazy("examination_tasks:add_section")

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds the page title to the template context.
        """
        data = super().get_context_data(**kwargs)
        data["title"] = _("Add New Section")
        return data

    def form_valid(self, form: SectionForm) -> HttpResponseRedirect:
        """
        Method for handling the form for adding examinations to the database
        """
        messages.success(self.request, _("Section added successfully!"))
        return super().form_valid(form)
