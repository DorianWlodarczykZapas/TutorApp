import os
import re
from typing import Optional

import pymupdf


class ExtractTaskFromPdf:

    @staticmethod
    def _validate_inputs(file_path: str, page_number: int) -> None:
        """Validates entry parameters."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

    @staticmethod
    def _get_page(doc: pymupdf.Document, page_number: int):
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

    @staticmethod
    def _find_grid_start(
        lines: list[str], start_index: int, threshold: int
    ) -> Optional[int]:
        """Find begin index of grid start in lines."""
        empty_count = 0

        for i in range(start_index + 1, len(lines)):
            line = lines[i].strip()

            if line == "" or line == " ":
                empty_count += 1
                if empty_count >= threshold:
                    return i - empty_count + 1
            else:

                if not ExtractTaskFromPdf._is_footer(line):
                    empty_count = 0

        return None

    @staticmethod
    def _is_footer(line: str) -> bool:
        """Checks if line is a footer."""
        footer_phrases = ["więcej arkuszy", "strona", "arkusze.pl"]
        return any(phrase in line.lower() for phrase in footer_phrases)

    @staticmethod
    def _get_y_coordinates(
        page, text_dict: dict, start_index: int, end_index: int, task_number: int
    ) -> tuple[float, float]:
        """Calculates y coordinates."""
        y_start, y_end = ExtractTaskFromPdf._get_y_from_text_dict(
            text_dict, start_index, end_index
        )

        if y_start is None:
            y_start = ExtractTaskFromPdf._get_y_from_search(page, task_number)

        if y_end is None:
            y_end = page.rect.height * 0.8

        margin = 5
        y_start = max(0, y_start - margin) if y_start else 0
        y_end = min(page.rect.height, y_end) if y_end else page.rect.height

        return y_start, y_end

    @staticmethod
    def _get_y_from_text_dict(
        text_dict: dict, start_index: int, end_index: int
    ) -> tuple[Optional[float], Optional[float]]:
        """Gets y coordinates."""
        y_start = None
        y_end = None
        line_counter = 0

        for block in text_dict["blocks"]:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                if line_counter == start_index and y_start is None:
                    y_start = line["bbox"][1]

                if line_counter == end_index and y_end is None:
                    y_end = line["bbox"][1]
                    break

                line_counter += 1

            if y_end is not None:
                break

        return y_start, y_end

    @staticmethod
    def _get_y_from_search(page, task_number: int) -> Optional[float]:
        """Finds y coordinates. by search te task"""
        text_instances = page.search_for(f"Zadanie {task_number}.")
        return text_instances[0].y0 if text_instances else None

    @staticmethod
    def _create_and_save_pdf(
        doc: pymupdf.Document,
        page,
        page_number: int,
        task_number: int,
        y_start: float,
        y_end: float,
        output_dir: str,
    ) -> str:
        """Creates new pdf of the task"""
        new_doc = pymupdf.open()
        new_page = new_doc.new_page(width=page.rect.width, height=y_end - y_start)

        clip_rect = pymupdf.Rect(0, y_start, page.rect.width, y_end)
        new_page.show_pdf_page(
            pymupdf.Rect(0, 0, page.rect.width, y_end - y_start),
            doc,
            page_number - 1,
            clip=clip_rect,
        )

        output_path = os.path.join(output_dir, f"zadanie {task_number}.pdf")
        new_doc.save(output_path, garbage=4, deflate=True)
        new_doc.close()

        return output_path

    class ExtractTaskFromPdf:

        @classmethod
        def extract_task(
            cls,
            file_path: str,
            task_number: int,
            page_number: int,
            output_dir: Optional[str] = None,
        ) -> str:
            """
            Main method to extract task from PDF.

            Args:
                file_path
                task_number
                page_number
                output_dir

            Returns:
                Path to extracted task
            """
            ExtractTaskFromPdf._validate_inputs(file_path, page_number)

            if output_dir is None:
                output_dir = os.path.dirname(file_path)

            doc = pymupdf.open(file_path)

            try:
                page = ExtractTaskFromPdf._get_page(doc, page_number)

                text = page.get_text()
                lines = text.split("\n")
                text_dict = page.get_text("dict")

                start_index = ExtractTaskFromPdf._find_task_start(lines, task_number)
                end_index = ExtractTaskFromPdf._find_task_end(
                    lines, start_index, task_number, grid_threshold=3
                )

                y_start, y_end = ExtractTaskFromPdf._get_y_coordinates(
                    page, text_dict, start_index, end_index, task_number
                )

                output_path = ExtractTaskFromPdf._create_and_save_pdf(
                    doc, page, page_number, task_number, y_start, y_end, output_dir
                )

                return output_path

            finally:
                doc.close()
