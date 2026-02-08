from typing import Any, Dict

from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.mixins import TeacherRequiredMixin
from videos.forms.video_form import AddVideoForm
from videos.forms.video_formset import VideoTimestampFormSet
from videos.models import Video


class VideoCreateView(TeacherRequiredMixin, CreateView):
    model = Video
    form_class = AddVideoForm
    template_name = "videos/add_video.html"
    success_url = reverse_lazy("videoos:add")

    def get_timestamp_formset(self, form=None):
        """Helper method to create and return a formset"""

        if self.request.POST:
            return VideoTimestampFormSet(
                self.request.POST, instance=form.instance if form else None
            )

        return VideoTimestampFormSet()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["timestamp_formset"] = self.get_timestamp_formset(
            form=kwargs.get("form")
        )
        return context

    def form_valid(self, form: AddVideoForm):

        timestamp_formset = self.get_timestamp_formset(form)

        if timestamp_formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                timestamp_formset.instance = self.object
                timestamp_formset.save()

            messages.success(
                self.request,
                _("Movie '%(title)s' added successfully!")
                % {"title": self.object.title},
            )
            return super().form_valid(form)

        else:
            return self.render_to_response(
                self.get_context_data(form=form, timestamp_formset=timestamp_formset)
            )
