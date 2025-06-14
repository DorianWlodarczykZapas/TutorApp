from django.urls import path
from .views import ExamCreateView

app_name = 'examination_tasks'

urlpatterns = [
    path('exams/add/', ExamCreateView.as_view(), name='exam_add'),

]
