from django.urls import path

from .views import AddMatriculationTaskView, ExamCreateView, SearchMatriculationTaskView

app_name = "examination_tasks"

urlpatterns = [
    path("exams/add/", ExamCreateView.as_view(), name="exam_add"),
    path(
        "exams/tasks/add/",
        AddMatriculationTaskView.as_view(),
        name="add_matriculation_task",
    ),
    path("tasks/search/", SearchMatriculationTaskView.as_view(), name="search_tasks"),
]
