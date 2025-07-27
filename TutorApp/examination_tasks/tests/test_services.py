from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model
from examination_tasks.services import MatriculationTaskService

User = get_user_model()


@pytest.fixture
def mock_exam():
    exam = Mock()
    exam.tasks_count = 5
    exam.tasks.values_list.return_value = [(1,), (3,), (5,)]
    return exam


class TestMatriculationTaskService:

    def test_get_missing_task_ids(self, mock_exam):
        result = MatriculationTaskService.get_missing_task_ids(mock_exam)
        assert result == [2, 4]
