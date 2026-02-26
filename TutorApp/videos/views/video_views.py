from typing import Any, Dict, Optional, Set

import django_filters
from courses.models import Section
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Page
from django.db import transaction
from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django_filters.views import FilterView
from plans.models import Plan, UserPlan
from users.mixins import TeacherRequiredMixin
from videos.forms.video_form import AddVideoForm, VideoFilterForm
from videos.forms.video_formset import VideoTimestampFormSet
from videos.models import Video, VideoTimestamp

from .filters import VideoFilterSet


class VideoCreateView(TeacherRequiredMixin, CreateView):
    model = Video
    form_class = AddVideoForm
    template_name = "videos/add_video.html"
    success_url = reverse_lazy("videos:add")

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

    def get_queryset(self) -> QuerySet[Video]:
        user = self.request.user

        try:
            user_plan = user.userplan
            is_premium_or_trial = user_plan.is_active and user_plan.plan.type in [
                Plan.PlanType.PREMIUM,
                Plan.PlanType.TRIAL,
            ]
        except UserPlan.DoesNotExist:
            is_premium_or_trial = False

        if is_premium_or_trial:
            return Video.objects.prefetch_related("timestamps")
        else:
            return Video.objects.prefetch_related(
                Prefetch(
                    "timestamps",
                    queryset=VideoTimestamp.objects.filter(
                        timestamp_type=VideoTimestamp.TimestampType.EXERCISE
                    ),
                )
            )
