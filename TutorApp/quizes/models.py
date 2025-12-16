from typing import List

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from examination_tasks import choices
from examination_tasks.models import Section


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

    def get_random_questions(self, number_of_questions: int) -> List["Question"]:
        """
        Return a list of randomly selected questions for  quiz.

        Args:
        number_of_questions: The number of questions to pick


        Returns:
        List of Question objects

        Raises:
            ValueError: If number_of_questions is not positive or exceeds available questions"

        """

        available_questions = self.questions.count()

        if number_of_questions <= 0:
            raise ValueError(_("Number of questions must be positive"))

        if number_of_questions > available_questions:
            raise ValueError(
                _(
                    "Cannot request %(requested)d questions. Only %(available)d available."
                )
                % {"requested": number_of_questions, "available": available_questions}
            )

        questions = self.questions.order_by("?")
        questions = questions[:number_of_questions]

        return list(questions)


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

        return List[Question]


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
    score = models.FloatField()
    max_score = models.IntegerField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user} - {self.quiz} - {self.score}/{self.max_score}"


class UserAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
    )
    selected_answers = models.ManyToManyField(
        Answer,
        related_name="user_quiz_answers",
    )
    points_earned = models.FloatField(default=0)

    class Meta:
        ordering = ["question__id"]
        unique_together = ["attempt", "question"]

    def __str__(self):
        return f"{self.attempt.user} - Q{self.question.id} - {self.points_earned}pts"
