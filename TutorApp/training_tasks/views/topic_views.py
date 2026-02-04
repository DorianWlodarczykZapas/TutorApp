from typing import Any, Dict

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.mixins import TeacherRequiredMixin

from TutorApp.examination_tasks.forms.topic_forms import TopicForm
from TutorApp.examination_tasks.models import Topic


class AddTopic(TeacherRequiredMixin, CreateView):
    """
    Simple view that adds topic to database via form
    """

    model = Topic
    form = TopicForm
    template_name = "examination_tasks/add_topic.html"
    success_url = reverse_lazy("examination_tasks:add_topic")

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds the page title to the template context.
        """
        data = super().get_context_data(**kwargs)
        data["title"] = _("Add New Topic")
        return data

    def form_valid(self, form: TopicForm) -> HttpResponseRedirect:
        """
        Method for handling the form for adding examinations to the database
        """
        messages.success(self.request, _("Topic added successfully!"))
        return super().form_valid(form)
