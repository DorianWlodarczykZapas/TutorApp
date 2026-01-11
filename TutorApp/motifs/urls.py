from django.urls import path

from .views.motif_views import AddMotifView, MotifListView, MotifDeleteView

app_name = "motifs"

urlpatterns = [
    path("add/", AddMotifView.as_view(), name="add_motif"),
    path("", MotifListView.as_view(), name="list_motifs"),
    path("<int:pk>/delete/", MotifDeleteView.as_view(), name="delete_motif"),
]
