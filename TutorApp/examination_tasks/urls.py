from django.urls import path

from TutorApp.training_tasks.views.book_views import AddBook
from TutorApp.training_tasks.views.section_views import AddSection
from TutorApp.training_tasks.views.topic_views import AddTopic
from TutorApp.training_tasks.views.training_task_views import (
    AddTrainingTask,
    TrainingTaskDetailView,
    TrainingTaskListView,
)

from .views.exam_task_views import (
    AddExamTaskWizard,
    ExamTaskListView,
    ExamTaskSearchEngine,
    TaskCutPdfStreamView,
    TaskDisplayView,
    TaskPdfView,
)
from .views.exam_views import AddExam, ExamListView, StudentProgressView

app_name = "examination_tasks"

urlpatterns = [
    path("exams/add/", AddExam.as_view(), name="exam_add"),
    path(
        "exams/tasks/add/",
        AddExamTaskWizard.as_view(),
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
    path("sections/add/", AddSection.as_view(), name="add_section"),
    path("topics/add/", AddTopic.as_view(), name="add_topic"),
    path("training-tasks/add/", AddTrainingTask.as_view(), name="add_training_task"),
    path(
        "training_tasks/<int:pk>/",
        TrainingTaskDetailView.as_view(),
        name="training_tasks_detail",
    ),
    path("training_tasks/", TrainingTaskListView.as_view(), name="training_tasks_list"),
    path("progress/", StudentProgressView.as_view(), name="student_progress"),
]
