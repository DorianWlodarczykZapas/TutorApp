import typing
from typing import TYPE_CHECKING, List, Optional

import fitz
from django.db.models import Count, F
from django.db.models.query import QuerySet
from users.models import User

if TYPE_CHECKING:
    from .models import Exam, MathMatriculationTasks


class MatriculationTaskService:
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
    def get_single_task_pdf(task_link: str, pages: list[int]) -> typing.Optional[bytes]:
        """
        The function from the given link to the PDF file extracts
        the pages specified as a list of integers and returns only those pages as bytes.

        :param task_link: Path to the source PDF file.
        :param pages: A list of page numbers to extract (1-based).
        :return: A bytes object representing the new PDF, or None if an error occurs or no pages are found.
        """
        task = fitz.open()
        try:
            with fitz.open(task_link) as exam:
                for page in pages:
                    page_index = page - 1
                    if 0 <= page_index < exam.page_count:
                        task.insert_pdf(exam, from_page=page_index, to_page=page_index)
                    else:
                        print(
                            f"Warning: Page number {page_index} is not found and going to be missed."
                        )

                if task.page_count > 0:
                    pdf_bytes = task.tobytes(garbage=4, deflate=True)
                    return pdf_bytes
                else:
                    return None
        except FileNotFoundError:
            print(f"Error: File not found under that path: {task_link}")
            return None
        except Exception as e:
            print(f"An unexpected error has occurred: {e}")
            return None
        finally:
            task.close()

    @staticmethod
    def _parse_pages_string(pages_str: str) -> List[int]:
        """
         Private helper method to convert the string “5-7” or “5”
        to a list of integers [5, 6, 7] or [5].
        """
        if not pages_str:
            return []
        try:
            if "-" in pages_str:
                start, end = map(int, pages_str.split("-"))
                return list(range(start, end + 1))
            else:
                return [int(pages_str)]
        except (ValueError, TypeError):
            return []
