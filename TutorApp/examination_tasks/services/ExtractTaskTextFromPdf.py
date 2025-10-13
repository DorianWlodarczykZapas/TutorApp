"""
PDF text extraction utility module.

This module provides functionality for extracting text content from PDF files
with support for selective page extraction and robust error handling.
"""

import os
from contextlib import contextmanager
from typing import Dict, List, Optional

try:
    import fitz
except ImportError:
    raise ImportError(
        "PyMuPDF is required for PDF text extraction. "
        "Install it with: pip install PyMuPDF"
    )


class ExtractTaskTextFromPdf:
    """
    A utility class for extracting text content from PDF files.

    Provides static methods for extracting text lines from PDF documents,
    with support for extracting from specific pages or entire documents.

    Example:
        >>> lines = ExtractTaskTextFromPdf.extract_lines("document.pdf", [1, 2, 3])
        >>> all_lines = ExtractTaskTextFromPdf.extract_all_lines("document.pdf")
        >>> text = ExtractTaskTextFromPdf.extract_text("document.pdf")
    """

    @staticmethod
    def extract_lines(
        file_path: str, page_numbers: Optional[List[int]] = None
    ) -> List[str]:
        """
        Extracts text from specified pages of a PDF file as a list of lines.

        Args:
            file_path (str): The path to the PDF file.
            page_numbers (Optional[List[int]]): A list of page numbers (1-based) from which
                                               to extract text. If None, extracts from all pages.

        Returns:
            List[str]: A list of strings, where each string is a line of text from
                      the selected pages. Returns an empty list if `page_numbers` is empty.

        Raises:
            TypeError: If input parameters are of incorrect type.
            FileNotFoundError: If the PDF file doesn't exist.
            ValueError: If page numbers are invalid or PDF processing fails.
        """
        ExtractTaskTextFromPdf._validate_file_path(file_path)

        with ExtractTaskTextFromPdf._open_pdf_document(file_path) as doc:

            if page_numbers is None:
                page_numbers = list(range(1, doc.page_count + 1))

            if not isinstance(page_numbers, list):
                raise TypeError("Page numbers must be provided as a list.")

            if not page_numbers:
                return []

            ExtractTaskTextFromPdf._validate_page_numbers(page_numbers, doc.page_count)
            return ExtractTaskTextFromPdf._extract_lines_from_pages(doc, page_numbers)

    @staticmethod
    def extract_all_lines(file_path: str) -> List[str]:
        """
        Extracts all text lines from a PDF file.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            List[str]: A list of all text lines from the PDF.
        """
        return ExtractTaskTextFromPdf.extract_lines(file_path, None)

    @staticmethod
    def extract_text(
        file_path: str, page_numbers: Optional[List[int]] = None, separator: str = "\n"
    ) -> str:
        """
        Extracts text from specified pages as a single string.

        Args:
            file_path (str): The path to the PDF file.
            page_numbers (Optional[List[int]]): Page numbers to extract from. If None, extracts all.
            separator (str): Separator to use when joining lines.

        Returns:
            str: The extracted text as a single string.
        """
        lines = ExtractTaskTextFromPdf.extract_lines(file_path, page_numbers)
        return separator.join(lines)

    @staticmethod
    def extract_lines_by_page(
        file_path: str, page_numbers: Optional[List[int]] = None
    ) -> Dict[int, List[str]]:
        """
        Extracts text from PDF organized by page number.

        Args:
            file_path (str): The path to the PDF file.
            page_numbers (Optional[List[int]]): Page numbers to extract from. If None, extracts all.

        Returns:
            Dict[int, List[str]]: A dictionary where keys are page numbers and values are lists of text lines.
        """
        ExtractTaskTextFromPdf._validate_file_path(file_path)

        with ExtractTaskTextFromPdf._open_pdf_document(file_path) as doc:
            if page_numbers is None:
                page_numbers = list(range(1, doc.page_count + 1))

            if not isinstance(page_numbers, list):
                raise TypeError("Page numbers must be provided as a list.")

            if not page_numbers:
                return {}

            ExtractTaskTextFromPdf._validate_page_numbers(page_numbers, doc.page_count)

            result = {}
            for page_num in page_numbers:
                result[page_num] = (
                    ExtractTaskTextFromPdf._extract_lines_from_single_page(
                        doc, page_num
                    )
                )

            return result

    @staticmethod
    def count_pages(file_path: str) -> int:
        """
        Counts the number of pages in a PDF file.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            int: The number of pages in the PDF.
        """
        ExtractTaskTextFromPdf._validate_file_path(file_path)

        with ExtractTaskTextFromPdf._open_pdf_document(file_path) as doc:
            return doc.page_count

    @staticmethod
    def _validate_file_path(file_path: str) -> None:
        """
        Validates that the file path is valid and the file exists.

        Args:
            file_path (str): The path to validate.

        Raises:
            TypeError: If file_path is not a string.
            FileNotFoundError: If the file doesn't exist.
        """
        if not isinstance(file_path, str):
            raise TypeError("File path must be a string.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: '{file_path}'")

    @staticmethod
    def _validate_page_numbers(page_numbers: List[int], total_pages: int) -> None:
        """
        Validates that all page numbers are valid for the document.

        Args:
            page_numbers (List[int]): List of page numbers to validate.
            total_pages (int): Total number of pages in the document.

        Raises:
            ValueError: If any page number is invalid.
        """
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

    @staticmethod
    @contextmanager
    def _open_pdf_document(file_path: str):
        """
        Context manager for safely opening and closing PDF documents.

        Args:
            file_path (str): Path to the PDF file.

        Yields:
            fitz.Document: The opened PDF document.

        Raises:
            ValueError: If the PDF cannot be opened or is corrupted.
        """
        doc = None
        try:
            doc = fitz.open(file_path)
            yield doc
        except fitz.errors.FitzError as e:
            raise ValueError(
                f"Error processing the PDF file: {e}. "
                f"The file may be corrupted or is not a valid PDF."
            )
        finally:
            if doc:
                doc.close()

    @staticmethod
    def _extract_lines_from_pages(doc, page_numbers: List[int]) -> List[str]:
        """
        Extracts text lines from specified pages of the document.

        Args:
            doc: The opened PDF document object.
            page_numbers (List[int]): List of page numbers (1-based) to extract from.

        Returns:
            List[str]: Combined list of text lines from all specified pages.
        """
        all_lines: List[str] = []

        for page_num in page_numbers:
            lines = ExtractTaskTextFromPdf._extract_lines_from_single_page(
                doc, page_num
            )
            all_lines.extend(lines)

        return all_lines

    @staticmethod
    def _extract_lines_from_single_page(doc, page_num: int) -> List[str]:
        """
        Extracts text lines from a single page.

        Args:
            doc: The opened PDF document object.
            page_num (int): Page number (1-based) to extract from.

        Returns:
            List[str]: List of text lines from the page.
        """
        page_index = page_num - 1
        page = doc.load_page(page_index)
        text = page.get_text("text")
        return text.splitlines()
