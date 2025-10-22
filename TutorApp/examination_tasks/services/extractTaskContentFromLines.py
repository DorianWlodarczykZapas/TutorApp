import re
from typing import Dict, List, Optional, Tuple


class ExtractTaskContentFromLines:
    """
    A utility class for extracting and cleaning the content of a specific task
    from a list of text lines.

    The class looks for task headers like: "Zadanie 3." and returns the cleaned
    content between that header and the next task header (or end of input).

    Example:
        >>> lines = [
        ...     "Zadanie 1.",
        ...     "Task 1 content",
        ...     "brudnopis",
        ...     "Zadanie 2.",
        ...     "Task 2 content",
        ... ]
        >>> ExtractTaskContentFromLines.get_clean_task_content(lines, 1)
        'Task 1 content'
    """

    TASK_START_PATTERN = re.compile(r"^\s*Zadanie\s+(\d+)\.")

    DEFAULT_FILTER_PHRASES = ("więcej arkuszy", "brudnopis")

    @staticmethod
    def get_clean_task_content(
        lines: List[str],
        task_number: int,
        filter_phrases: Optional[List[str]] = None,
    ) -> str:
        """
        Returns the cleaned content of the specified task as a single string.

        Args:
            lines (List[str]): List of text lines to search through.
            task_number (int): The task number to find.
            filter_phrases (Optional[List[str]]): Phrases to filter out (case-insensitive).
                                                 If None, default phrases are used.

        Returns:
            str: Cleaned task content as a single string.

        Raises:
            TypeError: If arguments have incorrect types.
            ValueError: If the task number is invalid or the task is not found.
        """
        ExtractTaskContentFromLines._validate_inputs(lines, task_number)

        task_indices = ExtractTaskContentFromLines._build_task_index(lines)

        start_idx, end_idx = ExtractTaskContentFromLines._find_task_boundaries(
            task_indices, task_number, len(lines)
        )

        raw_task_lines = ExtractTaskContentFromLines._slice_task_lines(
            lines, start_idx, end_idx
        )

        cleaned_lines = ExtractTaskContentFromLines._filter_and_clean_lines(
            raw_task_lines,
            filter_phrases or list(ExtractTaskContentFromLines.DEFAULT_FILTER_PHRASES),
        )

        return "\n".join(cleaned_lines)

    @staticmethod
    def _validate_inputs(lines: List[str], task_number: int) -> None:
        if not isinstance(lines, list):
            raise TypeError("Argument 'lines' must be a list of strings.")
        if not isinstance(task_number, int):
            raise TypeError("Argument 'task_number' must be an integer.")
        if task_number <= 0:
            raise ValueError("Task number must be a positive integer.")

    @staticmethod
    def _build_task_index(lines: List[str]) -> Dict[int, int]:
        """
        Builds a mapping: task_number -> start_index_in_lines.
        """
        task_indices: Dict[int, int] = {}
        for i, line in enumerate(lines):
            match = ExtractTaskContentFromLines.TASK_START_PATTERN.match(line)
            if match:
                found_task_num = int(match.group(1))
                task_indices[found_task_num] = i
        return task_indices

    @staticmethod
    def _find_task_boundaries(
        task_indices: Dict[int, int], task_number: int, total_lines: int
    ) -> Tuple[int, int]:
        """
        Determines the [start, end) range of lines belonging to the given task.
        """
        if task_number not in task_indices:
            raise ValueError(
                f"Task number {task_number} was not found in the provided text."
            )

        start_index = task_indices[task_number]

        next_indices = [idx for num, idx in task_indices.items() if num > task_number]
        end_index = min(next_indices) if next_indices else total_lines

        return start_index, end_index

    @staticmethod
    def _slice_task_lines(lines: List[str], start_idx: int, end_idx: int) -> List[str]:
        """
        Returns the lines belonging to the task (including the 'Zadanie X.' header).
        """
        return lines[start_idx:end_idx]

    @staticmethod
    def _filter_and_clean_lines(
        raw_task_lines: List[str], filter_phrases: List[str]
    ) -> List[str]:
        """
        Removes the 'Zadanie X.' header, trims whitespace, removes empty lines,
        and filters out any line containing specified phrases.
        """
        cleaned: List[str] = []
        for line in raw_task_lines[1:]:
            stripped = line.strip()
            if not stripped:
                continue

            lower = stripped.lower()
            if any(phrase in lower for phrase in filter_phrases):
                continue

            cleaned.append(stripped)

        return cleaned
