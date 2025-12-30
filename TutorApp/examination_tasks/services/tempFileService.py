import os

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
        pass

    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Moves the  temporary file

        Args:
            source_path : The path of the source file
            destination_path : The path of the destination

        Returns:
            Boolean indicating if the file was successfully transferred
        """
        pass

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
