from django.urls import path

from .views import QuizCreateView

app_name = "quizes"

urlpatterns = [
    path("add/", QuizCreateView.as_view(), name="add"),
]
