from django.urls import path
from videos.views.video_create_view import VideoCreateView

app_name = "videos"

urlpatterns = [
    path("add/", VideoCreateView.as_view(), name="add"),
]
