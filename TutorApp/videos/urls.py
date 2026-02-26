from django.urls import path
from videos.views.video_views import (
    SectionVideoListView,
    VideoCreateView,
    VideoDeleteView,
    VideoListView,
)

app_name = "videos"

urlpatterns = [
    path("", VideoListView.as_view(), name="video_list"),
    path("add/", VideoCreateView.as_view(), name="add"),
    path("delete/<int:pk>/", VideoDeleteView.as_view(), name="delete"),
    path(
        "sections/<int:section_pk>/videos/",
        SectionVideoListView.as_view(),
        name="section_videos",
    ),
]
