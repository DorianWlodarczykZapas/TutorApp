from django.urls import path

from .views.exam_task_views import AddExamTask
from .views.exam_views import AddExam
from .views.student_views import (
    ExamListView,
    ExamTaskListView,
    ExamTaskSearchEngine,
    TaskCutPdfStreamView,
    TaskDisplayView,
    TaskPdfView,
)
from .views.teacher_views import AddBook

app_name = "examination_tasks"

urlpatterns = [
    path("exams/add/", AddExam.as_view(), name="exam_add"),
    path(
        "exams/tasks/add/",
        AddExamTask.as_view(),
        name="add_exam_task",
    ),
    path("tasks/<int:pk>/pdf/", TaskPdfView.as_view(), name="task-pdf"),
    path("tasks/<int:pk>/", TaskDisplayView.as_view(), name="task-display"),
    path(
        "tasks/<int:pk>/pdf-stream/",
        TaskCutPdfStreamView.as_view(),
        name="task-pdf-stream",
    ),
    path(
        "tasks/<int:pk>/pdf-stream/<str:kind>/",
        TaskCutPdfStreamView.as_view(),
        name="task-pdf-stream-kind",
    ),
    path("exams/", ExamListView.as_view(), name="exam_list"),
    path(
        "exams/<int:exam_pk>/tasks/", ExamTaskListView.as_view(), name="exam_task_list"
    ),
    path("books/add/", AddBook.as_view(), name="add_book"),
    path(
        "task_search_engine/", ExamTaskSearchEngine.as_view(), name="task_search_engine"
    ),
]
