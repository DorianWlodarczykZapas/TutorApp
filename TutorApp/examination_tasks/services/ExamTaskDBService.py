from typing import TYPE_CHECKING, Dict, List, Optional, Set
from django.db.models import Count, F
from django.db.models.query import QuerySet
from users.models import User

if TYPE_CHECKING:
    from .models import Exam, MathMatriculationTasks


class ExamTaskDBService:
    @staticmethod
    def get_exams_with_available_tasks() -> QuerySet["Exam"]:
        """
        Returns a QuerySet of Exam instances that do not yet have all tasks added.
        The filtering is done at the database level for maximum efficiency.
        """
        from .models import Exam

        return Exam.objects.annotate(num_tasks=Count("tasks")).filter(
            tasks_count__gt=F("num_tasks")
        )

    @staticmethod
    def get_missing_task_ids(exam: "Exam") -> List[int]:
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
    ) -> QuerySet["MathMatriculationTasks"]:
        """
        Filters MathMatriculationTasks based on optional criteria.
        """
        from .models import MathMatriculationTasks

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

        return qs

    @staticmethod
    def get_user_completion_map_for_exams(
        user: "User", exams: List["Exam"]
    ) -> Dict[int, int]:
        """
        Calculates the number of completed tasks for a given user across a list of exams.

        This method is optimized to perform a single database query for all provided exams.

        Args:
            user: The user for whom to calculate completion.
            exams: A list or queryset of Exam objects.

        Returns:
            A dictionary mapping each exam's ID to the number of tasks
            completed by the user in that exam.
            Example: {101: 5, 102: 12, 105: 0}
        """

        if not user or not user.is_authenticated or not exams:
            return {}

        exam_ids = [exam.pk for exam in exams]

        from .models import MathMatriculationTasks

        completion_counts = (
            MathMatriculationTasks.objects.filter(
                exam_id__in=exam_ids, completed_by=user
            )
            .values("exam_id")
            .annotate(num_completed=Count("id"))
            .values_list("exam_id", "num_completed")
        )

        return dict(completion_counts)

    @staticmethod
    def get_task_completion_map(user: "User", exam: "Exam") -> Dict[int, bool]:
        """
        Creates a map of task completion statuses for a specific user and exam.

        This method is optimized to fetch all completed tasks for a user
        in a single database query.

        Args:
            user: The user for whom to check the completion status.
            exam: The specific Exam instance to check tasks against.

        Returns:
            A dictionary where keys are the `task_id`s from the MathMatriculationTasks
            model, and values are booleans (True if the user has completed the task,
            False otherwise).
            Example: {1: True, 2: False, 3: True, ...}
        """
        if not user or not user.is_authenticated:
            return {}

        from .models import MathMatriculationTasks

        completed_task_ids: Set[int] = set(
            MathMatriculationTasks.objects.filter(
                exam=exam, completed_by=user
            ).values_list("task_id", flat=True)
        )

        all_tasks_in_exam = exam.tasks.all()

        task_status_map: Dict[int, bool] = {
            task.task_id: (task.task_id in completed_task_ids)
            for task in all_tasks_in_exam
        }

        return task_status_map

    @staticmethod
    def toggle_completed(task: "MathMatriculationTasks", user: "User") -> bool:
        """
        Switches the task completion status for the user.

        Args:
            task (MathMatriculationTasks): Exam task.
            user (User): User.

        Returns:
            bool: True if the task is marked as completed, False if it is cancelled.
        """
        if task.completed_by.filter(id=user.id).exists():
            task.completed_by.remove(user)
            return False
        else:
            task.completed_by.add(user)
            return True