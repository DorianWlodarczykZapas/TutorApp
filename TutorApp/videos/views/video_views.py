from typing import Any, Dict, Optional, Set

import django_filters
from courses.models import Section
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Page
from django.db import transaction
from django.db.models import Prefetch, QuerySet
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, ListView
from django_filters.views import FilterView
from formtools.wizard.views import SessionWizardView
from plans.models import UserPlan
from users.mixins import TeacherRequiredMixin
from videos.filters import VideoFilterSet
from videos.forms.video_forms import (
    AddVideoStep1Form,
    AddVideoStep2Form,
    TimestampForm,
    VideoFilterForm,
)
from videos.models import Video, VideoTimestamp
from videos.services import YoutubeService


class VideoCreateWizard(TeacherRequiredMixin, SessionWizardView):

    form_list = [
        ("step_1", AddVideoStep1Form),
        ("step_2", AddVideoStep2Form),
    ]

    template_name = "videos/add_video_wizard.html"

    def done(self, form_list, **kwargs):
        step_1_data = self.get_cleaned_data_for_step("step_1")
        step_2_data = self.get_cleaned_data_for_step("step_2")

        TimestampFormSet = formset_factory(TimestampForm, extra=0)
        formset = TimestampFormSet(self.request.POST, prefix="timestamps")

        if not formset.is_valid():
            messages.error(
                self.request, _("Invalid timestamp data. Please check your changes.")
            )
            return redirect("videos:add_video")

        with transaction.atomic():
            video = Video.objects.create(
                title=step_2_data["title"],
                youtube_url=step_1_data["youtube_url"],
                section=step_1_data["section"],
                subject=step_1_data["subject"],
                level=step_1_data["level"],
            )

            for ts_form in formset:
                VideoTimestamp.objects.create(
                    video=video,
                    label=ts_form.cleaned_data["label"],
                    start_time=YoutubeService._parse_duration(
                        ts_form.cleaned_data["start_time"]
                    ),
                    timestamp_type=ts_form.cleaned_data["timestamp_type"],
                )

        messages.success(
            self.request,
            _("Movie '%(title)s' added successfully!") % {"title": video.title},
        )

        return redirect("videos:video_list")

    def process_step(self, form):
        if self.steps.current == "step_1":
            url = form.cleaned_data["youtube_url"]
            service = YoutubeService()
            data = service.extract_video_title_and_description(url)
            timestamps = service.parse_timestamps(data["description"])

            self.storage.extra_data["title"] = data["title"]
            self.storage.extra_data["timestamps"] = [
                {
                    "label": ts["label"],
                    "start_time": VideoTimestamp.format_duration(ts["start_time"]),
                    "timestamp_type": int(ts["timestamp_type"]),
                }
                for ts in timestamps
            ]

        return super().process_step(form)

    def get_context_data(self, form, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(form=form, **kwargs)

        if self.steps.current == "step_2":
            TimestampFormSet = formset_factory(TimestampForm, extra=0)
            initial_data = [
                {
                    "label": ts["label"],
                    "start_time": ts["start_time"],
                    "timestamp_type": ts["timestamp_type"],
                }
                for ts in self.storage.extra_data["timestamps"]
            ]

            if (
                self.request.method == "POST"
                and "timestamps-TOTAL_FORMS" in self.request.POST
            ):
                context["formset"] = TimestampFormSet(
                    self.request.POST, prefix="timestamps"
                )
            else:
                TimestampFormSet = formset_factory(TimestampForm, extra=0)
                data = {
                    "timestamps-TOTAL_FORMS": len(initial_data),
                    "timestamps-INITIAL_FORMS": len(initial_data),
                    "timestamps-MIN_NUM_FORMS": 0,
                    "timestamps-MAX_NUM_FORMS": 1000,
                }
                for i, ts in enumerate(initial_data):
                    data[f"timestamps-{i}-label"] = ts["label"]
                    data[f"timestamps-{i}-start_time"] = ts["start_time"]
                    data[f"timestamps-{i}-timestamp_type"] = ts["timestamp_type"]

                context["formset"] = TimestampFormSet(data, prefix="timestamps")
        return context

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == "step_2":
            initial["title"] = self.storage.extra_data.get("title", "")
        return initial


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

        return Video.objects.select_related("section").order_by(
            "section__name", "level", "title"
        )

    def _get_pagination_context(
        self, page_obj: Optional[Page], object_list
    ) -> Dict[str, Any]:
        """Extract pagination-related context data."""
        if page_obj:
            return {
                "total_count": page_obj.paginator.count,
                "current_page": page_obj.number,
                "total_pages": page_obj.paginator.num_pages,
                "start_idx": page_obj.start_index(),
                "end_idx": page_obj.end_index(),
            }

        total: int = len(object_list)
        return {
            "total_count": total,
            "current_page": 1,
            "total_pages": 1,
            "start_idx": 1 if total > 0 else 0,
            "end_idx": total,
        }

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)

        page_obj: Optional[Page] = context.get("page_obj")
        pagination_context = self._get_pagination_context(page_obj, self.object_list)
        context.update(pagination_context)

        filterset = context.get("filter")
        context["has_filters_applied"] = (
            self._are_filters_applied(filterset) if filterset else False
        )

        return context

    def _are_filters_applied(
        self, filterset: Optional[django_filters.FilterSet]
    ) -> bool:
        """
        Helper method for checking active filters.

        """
        if not filterset or not filterset.data:
            return False

        excluded_params: Set[str] = {"page", "csrfmiddlewaretoken"}

        return any(
            value and str(value).strip()
            for key, value in filterset.data.items()
            if key not in excluded_params
        )


class SectionVideoListView(LoginRequiredMixin, ListView):
    model = Video
    template_name = "videos/section_video_list.html"
    context_object_name = "videos"
    paginate_by = 20

    def get_queryset(self) -> QuerySet[Video]:
        self.section = get_object_or_404(Section, pk=self.kwargs["section_pk"])
        queryset = self.section.videos.all()
        form = VideoFilterForm(self.request.GET)
        if form.is_valid() and form.cleaned_data["title"]:
            queryset = queryset.filter(pk=form.cleaned_data["title"].pk)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["section"] = self.section
        context["form"] = VideoFilterForm(self.request.GET)
        return context


class VideoDetailsView(LoginRequiredMixin, DetailView):
    model = Video
    template_name = "videos/video_details.html"
    context_object_name = "video"

    def get_queryset(self) -> QuerySet[Video]:
        try:
            is_premium_or_trial = self.request.user.userplan.is_premium_or_trial
        except UserPlan.DoesNotExist:
            is_premium_or_trial = False

        if is_premium_or_trial:
            return Video.objects.prefetch_related("timestamps")

        return Video.objects.prefetch_related(
            Prefetch(
                "timestamps",
                queryset=VideoTimestamp.objects.filter(
                    timestamp_type=VideoTimestamp.TimestampType.EXERCISE
                ),
            )
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["timestamps"] = [
            {
                "label": ts.label,
                "seconds": ts.start_seconds,
                "time": ts.start_time_display,
                "type": ts.get_timestamp_type_display(),
                "timestamp_type": ts.timestamp_type,
            }
            for ts in self.object.timestamps.all()
        ]
        return context
