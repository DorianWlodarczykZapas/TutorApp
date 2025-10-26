from django.db import models
from examination_tasks.models import Section


class Quiz(models.Model):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="quiz_topics",
        verbose_name="Section",
    )
    question = models.CharField(max_length=255)
    question_picture = models.ImageField(
        upload_to="question_picture/", blank=True, null=True
    )
    explanation = models.TextField(blank=True, null=True)
    explanation_picture = models.ImageField(
        upload_to="explanation_picture/", blank=True, null=True
    )


class Answer(models.Model):
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"
