from typing import List, Optional

import fitz
import requests
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

    @staticmethod
    def extract_task_content(task: MathMatriculationTasks) -> str:
        """
        Downloads the exam PDF from `tasks_link` and extracts the content of the task
        identified by `task_id`. It searches for 'Zadanie {id}' and captures content
        until the next task or end of document.
        """
        url = task.exam.tasks_link
        task_marker = f"Zadanie {task.task_id}"
        next_task_marker = f"Zadanie {task.task_id + 1}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            return f"Failed to download PDF: {str(e)}"

        pdf_data = response.content

        try:
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            full_text = ""
            for page in doc:
                full_text += page.get_text()

            start = full_text.find(task_marker)
            if start == -1:
                return f"Task marker '{task_marker}' not found."

            end = full_text.find(next_task_marker, start)
            task_content = full_text[start:end] if end != -1 else full_text[start:]

            return task_content.strip()

        except Exception as e:
            return f"Error while processing PDF: {str(e)}"
