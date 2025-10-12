import os
import re
from typing import Optional

import fitz


class ExtractTaskFromPdf:

    @staticmethod
    def _validate_inputs(file_path: str, page_number: int) -> None:
        """Validates entry parameters."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

    @staticmethod
    def _get_page(doc: fitz.Document, page_number: int):
        """Gets page from pdf."""
        if page_number < 1 or page_number > doc.page_count:
            raise ValueError(f"Invalid page number: {page_number}")
        return doc.load_page(page_number - 1)

    @staticmethod
    def _find_task_start(lines: list[str], task_number: int) -> int:
        """Finds index of task start in lines."""
        task_pattern = re.compile(rf"^\s*Zadanie\s+{task_number}\.")

        for i, line in enumerate(lines):
            if task_pattern.match(line.strip()):
                return i

        raise ValueError(f"Task {task_number} not found.")

    @staticmethod
    def _find_task_end(
        lines: list[str], start_index: int, task_number: int, grid_threshold: int
    ) -> Optional[int]:
        """Finds index of task end in lines."""

        end_index = ExtractTaskFromPdf._find_next_task(lines, start_index, task_number)

        if end_index is None:
            end_index = ExtractTaskFromPdf._find_grid_start(
                lines, start_index, grid_threshold
            )

        return end_index if end_index is not None else len(lines)

    @staticmethod
    def _find_next_task(
        lines: list[str], start_index: int, current_task: int
    ) -> Optional[int]:
        """Finds next task."""
        next_task_pattern = re.compile(r"^\s*Zadanie\s+(\d+)\.")

        for i in range(start_index + 1, len(lines)):
            match = next_task_pattern.match(lines[i].strip())
            if match and int(match.group(1)) > current_task:
                return i

        return None
