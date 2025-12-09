from typing import List, Tuple


class QuizSolveService:
    """
    Class containing services related to solving quizzes:

        -method for collecting user responses
        -method for comparing user responses with answers to questions
        -method for calculating scores for a single question
        -method for saving user solutions to the database
    """

    def calculate_score(self, questions, user_answers) -> float:
        """
        Method for calculating the user's quiz score

        Args:
            questions (list): A list of the questions
            user_answers (list): A list of the user answers


        Returns:
            float: The user's quiz score
        """
        pass

    def get_user_answers(
        self, form_list: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """
        Method for getting the user answers

        Args:
        form_list (list): A list of the forms from wizard

        Returns:
        List[Tuple[str, str]]: A list of the user answers [quiz_question_id, user_answer]

        """
        pass
