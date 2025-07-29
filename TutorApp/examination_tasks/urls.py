from django.urls import path

from .views import (
    AddMatriculationTaskView,
    ExamCreateView,
    ExamProgressView,
    SearchMatriculationTaskView,
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
    path("tasks/search/", SearchMatriculationTaskView.as_view(), name="search_tasks"),
    path("progress/", ExamProgressView.as_view(), name="exam_progress"),
    path("tasks/<int:pk>/pdf/", TaskPdfView.as_view(), name="task-pdf"),
    path("tasks/<int:pk>/", TaskDisplayView.as_view(), name="task-display"),
    path(
        "tasks/<int:pk>/pdf-stream/",
        TaskPdfStreamView.as_view(),
        name="task-pdf-stream",
    ),
]
