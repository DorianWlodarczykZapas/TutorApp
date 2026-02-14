from typing import Any, Dict, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Page, Paginator
from django.db import transaction
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView
from django_filters.views import FilterView
from users.mixins import TeacherRequiredMixin
from videos.forms.video_form import AddVideoForm
from videos.forms.video_formset import VideoTimestampFormSet
from videos.models import Video

from .filters import VideoFilterSet


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


class VideoDeleteView(TeacherRequiredMixin, DeleteView):
    model = Video
    success_url = reverse_lazy("videos:list")


class VideoListView(LoginRequiredMixin, FilterView):

    model = Video
    filterset_class = VideoFilterSet
    template_name = "videos/video_list.html"
    paginate_by = 15
    context_object_name = "videos"

    def get_queryset(self) -> QuerySet[Video]:
        """
        Returns an optimized QuerySet with a forced sort order.

        Sort order:
        1. Section name (ascending)
        2. Difficulty level (defined in IntegerChoices)
        3. Title (alphabetical)
        """
        return Video.objects.select_related("section").order_by(
            "section__name", "level", "title"
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:

        context: Dict[str, Any] = super().get_context_data(**kwargs)

        page_obj: Optional[Page] = context.get("page_obj")

        if page_obj:
            paginator: Paginator = page_obj.paginator
            context["total_count"] = paginator.count
            context["current_page"] = page_obj.number
            context["total_pages"] = paginator.num_pages
        else:

            context["total_count"] = len(self.object_list)
            context["current_page"] = 1
            context["total_pages"] = 1

        filterset = context.get("filter")
        context["has_filters_applied"] = (
            self._are_filters_applied(filterset) if filterset else False
        )

        return context

    def _are_filters_applied(self, filterset) -> bool:
        """
        Helper method for checking active filters.

        """
        excluded_params = {"page", "csrfmiddlewaretoken"}

        return any(
            value and str(value).strip()
            for key, value in filterset.data.items()
            if key not in excluded_params
        )
