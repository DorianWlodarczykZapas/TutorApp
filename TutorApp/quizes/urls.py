from django.urls import path

from .views.quiz_views import AddQuiz, QuizList

app_name = "quizes"

urlpatterns = [
    path("add/", AddQuiz.as_view(), name="add_quiz"),
    path("", QuizList.as_view(), name="quiz_list"),
]
