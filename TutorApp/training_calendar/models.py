# training_calendar/models.py
from django.db import models
from django.conf import settings
from datetime import date


class StudyPlan(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    tasks_per_day = models.PositiveIntegerField(
        default=5,
        help_text="Number of math tasks per day"
    )
    start_date = models.DateField(default=date.today)
    exam_date = models.DateField()

    @property
    def days_left(self):
        return (self.exam_date - date.today()).days


class DailyStudy(models.Model):
    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name='daily_records')
    date = models.DateField()
    warmups = models.PositiveIntegerField(default=0)
    exam_tasks = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('plan', 'date')


class ScheduledTask(models.Model):
    daily = models.ForeignKey(DailyStudy, on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey('examination_tasks.MathMatriculationTasks',
                             on_delete=models.CASCADE)
    is_warmup = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
