from django.urls import path

from .views.question_views import AddQuestion
from .views.quiz_views import AddQuiz, QuizList

app_name = "quizes"

urlpatterns = [
    path("add/", AddQuiz.as_view(), name="add_quiz"),
    path("", QuizList.as_view(), name="quiz_list"),
    path(
        "quiz/<int:quiz_pk>/add-question/", AddQuestion.as_view(), name="add_question"
    ),
]
