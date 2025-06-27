from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from users.services import UserService

from .forms import AddVideoForm
from .models import Video


class VideoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Video
    form_class = AddVideoForm
    template_name = "videos/video_form.html"
    success_url = reverse_lazy("video_form")

    def test_func(self) -> bool:
        return UserService(self.request.user).is_teacher()

    def form_valid(self, form: AddVideoForm) -> Any:
        return super().form_valid(form)


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
