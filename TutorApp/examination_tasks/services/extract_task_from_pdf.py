import os

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
