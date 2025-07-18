from django.urls import path

from .views import CategorySelectView, QuizCreateView

app_name = "quizes"

urlpatterns = [
    path("add/", QuizCreateView.as_view(), name="add"),
    path("", CategorySelectView.as_view(), name="category"),
]
