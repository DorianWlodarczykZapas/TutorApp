import logging
import re
from datetime import timedelta
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from users.services import UserService

from .forms import AddVideoForm
from .models import Video, VideoTimestamp

logger = logging.getLogger(__name__)


class VideoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Video
    form_class = AddVideoForm
    template_name = "videos/video_form.html"
    success_url = reverse_lazy("video_form")

    def test_func(self):
        return UserService(self.request.user).is_teacher()

    def form_valid(self, form):
        response = super().form_valid(form)

        timestamps_raw = self.request.POST.get("timestamp_block", "").strip()
        lines = timestamps_raw.splitlines()

        current_type = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("ćwiczenia"):
                current_type = VideoTimestamp.TimestampType.EXERCISE
            elif line.lower().startswith("zadania"):
                current_type = VideoTimestamp.TimestampType.TASK
            else:
                match = re.match(r"(\d{1,2}:\d{2})(?:[:\d{2}]*)\s+(.*)", line)
                if match:
                    time_str, label = match.groups()
                    try:
                        h, m, s = (
                            list(map(int, (time_str + ":00").split(":"))) + [0, 0]
                        )[:3]
                        duration = timedelta(hours=h, minutes=m, seconds=s)
                        VideoTimestamp.objects.create(
                            video=self.object,
                            label=label,
                            start_time=duration,
                            type=current_type or VideoTimestamp.TimestampType.EXERCISE,
                        )
                    except Exception as e:
                        logger.warning(f"Błąd przy przetwarzaniu linii '{line}': {e}")
                        continue
        return response


class SectionListView(ListView):
    template_name = "videos/section_list.html"
    context_object_name = "sections"

    def get_queryset(self) -> Any:
        return (
            Video.objects.values("type")
            .annotate(video_count=Count("id"))
            .order_by("type")
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["section_labels"] = dict(Video.section)
        return context


class SubcategoryListView(ListView):
    template_name = "videos/subcategory_list.html"
    context_object_name = "subcategories"

    def get_queryset(self) -> Any:
        section_id = self.kwargs["section_id"]
        return (
            Video.objects.filter(type=section_id)
            .values("subcategory")
            .annotate(video_count=Count("id"))
            .order_by("subcategory")
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        section_id = self.kwargs["section_id"]
        context["section_id"] = section_id
        context["section_name"] = dict(Video.section).get(int(section_id), "")
        return context


class VideoListView(ListView):
    template_name = "videos/video_list.html"
    context_object_name = "videos"

    def get_queryset(self) -> Any:
        section_id = self.kwargs["section_id"]
        subcategory = self.kwargs["subcategory"]
        return Video.objects.filter(type=section_id, subcategory=subcategory)

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        section_id = self.kwargs["section_id"]
        context["section_name"] = dict(Video.section).get(int(section_id), "")
        context["subcategory"] = self.kwargs["subcategory"]
        return context
