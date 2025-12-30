import os
import shutil

from ..models import Exam


class TempFileService:
    """
    Class containing services related to temporary files.
        -method for creating a temporary directory
        -method for transferring the temporary file
        -method for recreating the directory
        -method for building the final path
    """

    def create_temp_directory(self, path: str) -> str:
        """
        Creates a temporary directory if not exists

        Args:
            path : The path of the directory

        Returns:
            The path of the directory

        """

        os.makedirs(path, exist_ok=True)

        return path

    def move_file(self, source_path: str, destination_path: str) -> str:
        """
        Moves the  temporary file

        Args:
            source_path : The path of the source file
            destination_path : The path of the destination

        Returns:
            Path to the moved file (typically same as destination_path)

        Raises:
            FileNotFoundError: If source_path does not exist
            OSError: If move fails (permissions, disk space, etc.)
        """

        return shutil.move(source_path, destination_path)

    def recreate_directory(self, path: str) -> None:
        """
        Removes directory and recreates it empty

        Args:
             path: The path of the directory


        Raises:
        OSError: If directory cannot be removed or recreated
        """
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

    def build_final_path(
        self, exam: Exam, task_id: int, media_root: str, base_dir: str = "exam_tasks"
    ) -> str:
        """
        Builds the final path of the temporary file

        Args:
            exam : The exam object
            task_id : The task id
            media_root: Root media directory (e.g., settings.MEDIA_ROOT)
            base_dir : The base directory


        Returns:
            The final path of the  file

        """

        return os.path.join(
            media_root,
            base_dir,
            str(exam.subject.name),
            str(exam.exam_type),
            str(exam.year),
            str(exam.month),
            f"zadanie_{task_id}.pdf",
        )
