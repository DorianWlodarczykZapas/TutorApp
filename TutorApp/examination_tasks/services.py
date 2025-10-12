import os
import re
import typing
from typing import Dict, List

import fitz


class MatriculationTaskService:

    @staticmethod
    def get_single_task_pdf(task_link: str, pages: list[int]) -> typing.Optional[bytes]:
        """
        The function from the given link to the PDF file extracts
        the pages specified as a list of integers and returns only those pages as bytes.
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

            print(f"An unexpected error has occurred inside PyMuPDF: {e}")
            print(f"Typ błędu: {type(e)}")
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
                if start > end:
                    return []
                return list(range(start, end + 1))
            else:
                return [int(pages_str)]
        except (ValueError, TypeError):
            return []

    @staticmethod
    def extract_text_lines_from_pdf(
        file_path: str, page_numbers: List[int]
    ) -> List[str]:
        """
        Extracts text from specified pages of a PDF file as a list of lines.

        Args:
            file_path (str): The path to the PDF file.
            page_numbers (List[int]): A sorted list of page numbers (1-based) from which
                                      to extract text.

        Returns:
            List[str]: A list of strings, where each string is a line of text from
                       the selected pages. Returns an empty list if `page_numbers` is empty.

        """
        if not isinstance(file_path, str):
            raise TypeError("File path must be a string.")
        if not isinstance(page_numbers, list):
            raise TypeError("Page numbers must be provided as a list.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: '{file_path}'")

        if not page_numbers:
            return []

        doc = None
        try:
            doc = fitz.open(file_path)

            total_pages = doc.page_count
            if total_pages == 0:
                raise ValueError("The PDF file is empty (contains no pages).")

            for num in page_numbers:
                if not isinstance(num, int):
                    raise ValueError(
                        f"Page numbers list contains a non-integer value: '{num}'."
                    )
                if not (1 <= num <= total_pages):
                    raise ValueError(
                        f"Invalid page number: {num}. The document has {total_pages} pages "
                        f"(valid range is 1 to {total_pages})."
                    )

            all_lines: List[str] = []
            for page_num in page_numbers:
                page_index = page_num - 1
                page = doc.load_page(page_index)
                text = page.get_text("text")

                lines_from_page = text.splitlines()
                all_lines.extend(lines_from_page)

            return all_lines

        except fitz.errors.FitzError as e:

            raise ValueError(
                f"Error processing the PDF file: {e}. "
                f"The file may be corrupted or is not a valid PDF."
            )

        finally:

            if doc:
                doc.close()

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
