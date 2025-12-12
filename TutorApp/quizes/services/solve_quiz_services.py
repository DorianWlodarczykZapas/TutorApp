from typing import List, Tuple

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from users.models import User

from ..models import Question, Quiz, QuizAttempt


class QuizSolveService:
    """
    Class containing services related to solving quizzes:


        -method for comparing user responses with answers to questions
        -method for calculating scores for a single question
        -method for calculating scores for quiz
        -method for saving user solutions to the database
    """

    def calculate_score(
        self, questions: List[Question], user_answers: List[Tuple[str, List[int]]]
    ) -> float:
        """
        Method for calculating the user's quiz score

        Args:
            questions : A list of the question objects
            user_answers : List of tuples (question_id, list of selected answer IDs)
                  Example: [("question_5", [10, 12]), ("question_7", [20])]


        Returns:
             The user's quiz score

        Raises:
            ValueError: If question_id in question_map does not exist
        """

        question_map = {question.id: question for question in questions}

        total_score = 0.0

        for question_id_str, selected_ids in user_answers:
            question_id_int = int(question_id_str.split("_")[1])

            if question_id_int not in question_map:
                raise ValueError(
                    _("Question %(id)s does not exist") % {"id": question_id_int}
                )

            question = question_map[question_id_int]

            score = self.calculate_question_score(question, selected_ids)

            total_score += score

        total_score = round(total_score, 2)

        return total_score

    def calculate_question_score(
        self, question: Question, selected_answer_ids: List[int]
    ) -> float:
        """
        A method that compares the user's answers with the correct answers for a given question.


        Args:
            question : A question object
            selected_answer_ids: List of Answer IDs that user selected for this question

        Returns:

             The user's question score

        Raises:
            ValueError: If question doesn't have both correct and incorrect answers
        """

        correct_answers = question.answers.filter(is_correct=True)
        incorrect_answers = question.answers.filter(is_correct=False)

        correct_ids = [answer.id for answer in correct_answers]
        incorrect_ids = [answer.id for answer in incorrect_answers]

        if len(correct_ids) == 0 or len(incorrect_ids) == 0:
            raise ValueError(_("Question must have both correct and incorrect answers"))

        points_per_correct = 1.0 / len(correct_ids)

        points_per_incorrect = 1.0 / len(incorrect_ids)

        earned_points = 0.0

        for answer_id in selected_answer_ids:
            if answer_id in correct_ids:
                earned_points += points_per_correct
            elif answer_id in incorrect_ids:
                earned_points -= points_per_incorrect

        earned_points = max(0, earned_points)

        earned_points = round(earned_points, 2)

        return earned_points

    def save_quiz_attempt(
        self,
        user: User,
        quiz: Quiz,
        score: float,
        max_score: float,
    ) -> QuizAttempt:
        """
        Creates and save QuizAttempt object

        Args:
            user: The user object
            quiz: The quiz object
            score: The user's quiz score
            max_score: The quiz max possible score



        Returns:
            QuizAttempt: A QuizAttempt object

        Raises:
            ValueError: If score is negative, max_score is not positive,
                or score exceeds max_score
        """

        if score < 0:
            raise ValueError(_("Score cannot be negative"))

        if max_score <= 0:
            raise ValueError(_("Max score must be positive"))

        if score > max_score:
            raise ValueError(_("Score cannot be greater than max score"))

        quiz_attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            score=score,
            max_score=max_score,
            completed_at=timezone.now(),
        )

        return quiz_attempt

    def save_user_answers(
        self, quiz_attempt: QuizAttempt, user_answers: List[Tuple[str, List[int]]]
    ) -> None:
        """
        Save UserAnswers for existing QuizAttempt

        Args:
            quiz_attempt : A QuizAttempt object
            user_answers: List of tuples (question_id, list of selected answer IDs)
              Example: [("question_5", [10, 12]), ("question_7", [20])]

        """
        pass
