from django.urls import path
from views.motif_views import AddMotifView

app_name = "motifs"

urlpatterns = [
    path("add/", AddMotifView.as_view(), name="add_motif"),
]
