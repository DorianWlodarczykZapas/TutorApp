import typing
from typing import TYPE_CHECKING, List, Optional

import fitz
import requests
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
    def populate_task_content(task: "MathMatriculationTasks") -> None:
        """
        Extracts task content from a PDF and sets the `content` attribute
        on the provided task instance. It does not save the instance.
        In case of an error, the error message is stored in the content field.
        """

        if not task.exam or not task.exam.tasks_link:
            task.content = "Error: Exam or tasks_link is missing."
            return

        url = task.exam.tasks_link
        task_marker = f"Zadanie {task.task_id}"
        next_task_marker = f"Zadanie {task.task_id + 1}"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            pdf_data = response.content

            doc = fitz.open(stream=pdf_data, filetype="pdf")
            full_text = "".join(page.get_text() for page in doc)
            doc.close()

            start_pos = full_text.find(task_marker)
            if start_pos == -1:
                task.content = f"Error: Task marker '{task_marker}' not found."
                return

            end_pos = full_text.find(next_task_marker, start_pos)

            if end_pos == -1:
                task.content = full_text[start_pos:].strip()
            else:
                task.content = full_text[start_pos:end_pos].strip()

        except Exception as e:
            task.content = f"Error while processing PDF: {str(e)}"

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
