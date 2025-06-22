from django.urls import path

from TutorApp.videos.views import VideoCreateView

app_name = "videos"

urlpatterns = [
    path("add/", VideoCreateView.as_view(), name="add"),
]
