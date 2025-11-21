from django.urls import path

from .views.quiz_views import AddQuiz

app_name = "quizes"

urlpatterns = [
    path("add/", AddQuiz.as_view(), name="add_quiz"),
]
