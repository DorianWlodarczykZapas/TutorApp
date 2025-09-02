from django.urls import path

from .views import (
    AddMatriculationTaskView,
    ExamCreateView,
    ExamListView,
    ExamTaskListView,
    TaskDisplayView,
    TaskPdfStreamView,
    TaskPdfView,
)

app_name = "examination_tasks"

urlpatterns = [
    path("exams/add/", ExamCreateView.as_view(), name="exam_add"),
    path(
        "exams/tasks/add/",
        AddMatriculationTaskView.as_view(),
        name="add_matriculation_task",
    ),
    path("tasks/<int:pk>/pdf/", TaskPdfView.as_view(), name="task-pdf"),
    path("tasks/<int:pk>/", TaskDisplayView.as_view(), name="task-display"),
    path(
        "tasks/<int:pk>/pdf-stream/",
        TaskPdfStreamView.as_view(),
        name="task-pdf-stream",
    ),
    path("exams/", ExamListView.as_view(), name="exam_list"),
    path(
        "exams/<int:exam_pk>/tasks/", ExamTaskListView.as_view(), name="exam_task_list"
    ),
]
