from typing import List

from .models import Exam


class MatriculationTaskService:
    @staticmethod
    def get_exams_with_available_tasks() -> List[Exam]:
        """
        Returns a list of Exam instances that do not yet have all tasks added.
        Only exams where the number of related MathMatriculationTasks is less than tasks_count.
        """
        exams = Exam.objects.all()
        return [exam for exam in exams if exam.tasks.count() < exam.tasks_count]
