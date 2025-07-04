from typing import List, Optional

from users.models import User

from .models import Exam, MathMatriculationTasks


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

    @staticmethod
    def filter_tasks(
        year: Optional[int] = None,
        month: Optional[int] = None,
        level: Optional[int] = None,
        category: Optional[int] = None,
        is_done: Optional[bool] = None,
        user: Optional[User] = None,
    ) -> List[MathMatriculationTasks]:
        """
        Filters MathMatriculationTasks based on optional criteria:
        - year: exam year
        - month: exam month
        - level: task difficulty level (1: Basic, 2: Extended)
        - category: task category ID
        - is_done: whether the task has been completed by the given user
        - user: user instance to check completion status

        Returns a list of MathMatriculationTasks that match the given criteria.
        If no filters are provided, all tasks are returned.
        """
        qs = MathMatriculationTasks.objects.select_related("exam").all()

        if year is not None:
            qs = qs.filter(exam__year=year)
        if month is not None:
            qs = qs.filter(exam__month=month)
        if level is not None:
            qs = qs.filter(type=level)
        if category is not None:
            qs = qs.filter(category=category)
        if is_done is not None and user is not None:
            if is_done:
                qs = qs.filter(done_by=user)
            else:
                qs = qs.exclude(done_by=user)

        return list(qs)
