from django.urls import path

from TutorApp.training_tasks.views.book_views import AddBook
from TutorApp.training_tasks.views.section_views import AddSection
from TutorApp.training_tasks.views.topic_views import AddTopic
from TutorApp.training_tasks.views.training_task_views import (
    AddTrainingTask,
    TrainingTaskDetailView,
    TrainingTaskListView,
)

app_name = "examination_tasks"

urlpatterns = [
    path("books/add/", AddBook.as_view(), name="add_book"),
    path("sections/add/", AddSection.as_view(), name="add_section"),
    path("topics/add/", AddTopic.as_view(), name="add_topic"),
    path("training-tasks/add/", AddTrainingTask.as_view(), name="add_training_task"),
    path(
        "training_tasks/<int:pk>/",
        TrainingTaskDetailView.as_view(),
        name="training_tasks_detail",
    ),
    path("training_tasks/", TrainingTaskListView.as_view(), name="training_tasks_list"),
]
