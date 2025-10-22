import typing

import pymupdf


class ExtractTaskPagesFromPdf:
    @staticmethod
    def get_single_task_pdf(task_link: str, pages: list[int]) -> typing.Optional[bytes]:
        """
        The function from the given link to the PDF file extracts
        the pages specified as a list of integers and returns only those pages as bytes.
        """

        task = pymupdf.open()
        try:

            with pymupdf.open(task_link) as exam:

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
