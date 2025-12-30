import os
import shutil

from ..models import Exam


class TempFileService:
    """
    Class containing services related to temporary files.
        -method for creating a temporary directory
        -method for transferring the temporary file
        -method for cleaning the directory
        -method for checking if the file exists
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

    def cleanup_directory(self, path: str) -> bool:
        """
        Cleans the temporary directory

        Args:
             path: The path of the directory

        Returns:
            Boolean indicating if the file was successfully cleaned
        """
        pass

    def file_exists(self, path: str) -> bool:
        """
        Checks if the temporary file exists

        Args:
            path: The path of the temporary file

        Returns:
            Boolean indicating if the temporary file exists


        """
        return os.path.exists(path)

    def build_final_path(self, exam: Exam, task_id: int) -> str:
        """
        Builds the final path of the temporary file

        Args:
            exam : The exam object
            task_id : The task id

        Returns:
            The final path of the temporary file

        """
        pass
