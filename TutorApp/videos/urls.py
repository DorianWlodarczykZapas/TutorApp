from django.urls import path

from .views import SectionListView, VideoCreateView

app_name = "videos"

urlpatterns = [
    path("add/", VideoCreateView.as_view(), name="add"),
    path("", SectionListView.as_view(), name="section_list"),
]
