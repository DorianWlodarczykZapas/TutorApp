import os


class ExtractTaskFromPdf:

    @staticmethod
    def _validate_inputs(file_path: str, page_number: int) -> None:
        """Validates entry parameters."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
