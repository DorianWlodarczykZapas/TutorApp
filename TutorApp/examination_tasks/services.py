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

    @staticmethod
    def get_missing_task_ids(exam: Exam) -> List[int]:
        """
        Returns a list of missing task IDs for a given exam.
        """
        existing_ids = set(exam.tasks.values_list("task_id", flat=True))
        all_ids = set(range(1, exam.tasks_count + 1))
        return sorted(list(all_ids - existing_ids))
