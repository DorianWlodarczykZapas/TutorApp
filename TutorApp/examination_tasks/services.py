import re
from typing import Dict, List


class MatriculationTaskService:

    @staticmethod
    def get_clean_task_content(lines: List[str], task_number: int) -> str:
        """
        Searches for the content of a specific task, cleans it of unnecessary elements
        and returns it as a single string.


        Args:
            lines (List[str]): A list of strings (lines of text) to search.
            task_number (int): The number of the task to find.

        Returns:
            str: The cleaned task content as a single string.


        """

        if not isinstance(lines, list):
            raise TypeError("Argument 'lines' musi być listą stringów.")
        if not isinstance(task_number, int):
            raise TypeError("Argument 'task_number' musi być liczbą całkowitą.")
        if task_number <= 0:
            raise ValueError("Numer zadania musi być liczbą dodatnią.")

        task_start_pattern = re.compile(r"^\s*Zadanie\s+(\d+)\.")

        task_indices: Dict[int, int] = {}
        for i, line in enumerate(lines):
            match = task_start_pattern.match(line)
            if match:
                found_task_num = int(match.group(1))
                task_indices[found_task_num] = i

        if task_number not in task_indices:
            raise ValueError(
                f"Zadanie numer {task_number} nie zostało znalezione w podanym tekście."
            )

        start_index = task_indices[task_number]
        end_index = len(lines)

        next_task_start_index = float("inf")
        for num, index in task_indices.items():
            if num > task_number and index < next_task_start_index:
                next_task_start_index = index

        if next_task_start_index != float("inf"):
            end_index = next_task_start_index

        raw_task_lines = lines[start_index:end_index]

        cleaned_lines = []

        filter_phrases = ["więcej arkuszy", "brudnopis"]

        for line in raw_task_lines[1:]:
            stripped_line = line.strip()

            if stripped_line and not any(
                phrase in stripped_line.lower() for phrase in filter_phrases
            ):
                cleaned_lines.append(stripped_line)

        return "\n".join(cleaned_lines)
