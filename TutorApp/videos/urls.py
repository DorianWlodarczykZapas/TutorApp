from django.urls import path

from .views import SectionListView, SubcategoryListView, VideoCreateView, VideoListView

app_name = "videos"

urlpatterns = [
    path("add/", VideoCreateView.as_view(), name="add"),
    path("", SectionListView.as_view(), name="section_list"),
    path(
        "section/<int:section_id>/",
        SubcategoryListView.as_view(),
        name="subcategory_list",
    ),
    path(
        "section/<int:section_id>/<str:subcategory>/",
        VideoListView.as_view(),
        name="video_list",
    ),
]
