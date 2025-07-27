from unittest.mock import Mock, patch

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

    @patch("services.MathMatriculationTasks.objects.select_related")
    def test_filter_tasks_by_year(self, mock_select_related):
        mock_qs = Mock()
        mock_select_related.return_value.all.return_value = mock_qs
        mock_qs.filter.return_value = "filtered"

        result = MatriculationTaskService.filter_tasks(year=2021)
        assert result == "filtered"

    def test_populate_task_content_missing_link(self):
        task = Mock()
        task.exam = None
        MatriculationTaskService.populate_task_content(task)
        assert "missing" in task.content.lower()
