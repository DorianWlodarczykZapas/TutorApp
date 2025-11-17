from django.conf import settings
from django.db import models
from examination_tasks.models import Section

from TutorApp.examination_tasks import choices


class Quiz(models.Model):
    title = models.CharField(max_length=100)
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name="Section",
    )

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ["section", "title"]

    def __str__(self):
        return f"{self.title} {self.section}"


class Question(models.Model):
    text = models.TextField()
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Quiz",
    )
    level_type = models.IntegerField(
        choices=choices.LEVEL_CHOICES,
        null=True,
        blank=True,
        help_text="Level of question. Can be Basic or Extended",
    )

    picture = models.ImageField(upload_to="question_picture/", blank=True, null=True)
    explanation = models.TextField(blank=True)
    explanation_picture = models.ImageField(
        upload_to="explanation_picture/", blank=True, null=True
    )

    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    score = models.IntegerField()
    max_score = models.IntegerField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user} - {self.quiz} - {self.score}/{self.max_score}"
