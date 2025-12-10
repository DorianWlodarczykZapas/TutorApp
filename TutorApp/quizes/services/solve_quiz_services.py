from typing import List, Tuple

from django.forms import Form
from users.models import User

from ..models import Question, Quiz, QuizAttempt


class QuizSolveService:
    """
    Class containing services related to solving quizzes:

        -method for collecting user responses
        -method for comparing user responses with answers to questions
        -method for calculating scores for a single question
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
        """
        pass

    def get_user_answers(self, form_list: List[Form]) -> List[Tuple[str, List[int]]]:
        """
        Method for getting the user answers

        Args:
        form_list : A list of  form steps from wizard

        Returns:
        A list of the user answers [quiz_question_id, user_answer]

        """
        pass

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
        """

        pass

    def save_quiz_attempt(
        self,
        user: User,
        quiz: Quiz,
        score: float,
        user_answers: List[Tuple[str, List[int]]],
    ) -> QuizAttempt:
        """
        Creates and save QuizAttempt object

        Args:
            user: The user object
            quiz: The quiz object
            score: The user's quiz score
            List of tuples (question_id, list of selected answer IDs)
                  Example: [("question_5", [10, 12]), ("question_7", [20])]


        Returns:
            QuizAttempt: A QuizAttempt object
        """

        pass

    def save_user_answers(
        self, quiz_attempt: QuizAttempt, user_answers: List[Tuple[str, List[int]]]
    ) -> None:
        """
        Save UserAnswers for existing QuizAttempt

        Args:
            quiz_attempt : A QuizAttempt object
            List of tuples (question_id, list of selected answer IDs)
                  Example: [("question_5", [10, 12]), ("question_7", [20])]

        """
        pass
