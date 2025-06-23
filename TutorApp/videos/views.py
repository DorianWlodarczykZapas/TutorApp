from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
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
