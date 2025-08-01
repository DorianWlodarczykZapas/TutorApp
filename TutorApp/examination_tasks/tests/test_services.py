from unittest.mock import MagicMock, Mock, patch

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

    @patch("services.fitz.open")
    @patch("services.requests.get")
    def test_populate_task_content_success(self, mock_get, mock_fitz):
        # Mock task
        task = Mock()
        task.task_id = 1
        task.exam = Mock()
        task.exam.tasks_link = "http://example.com/sample.pdf"

        mock_response = Mock()
        mock_response.content = b"%PDF mock"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_page = Mock()
        mock_page.get_text.return_value = (
            "Zadanie 1\nTo jest treść zadania\nZadanie 2\n"
        )
        mock_doc = [mock_page]
        mock_fitz.return_value = mock_doc

        MatriculationTaskService.populate_task_content(task)
        assert "To jest treść zadania" in task.content

    @patch("services.requests.get")
    def test_populate_task_content_pdf_exception(self, mock_get):
        task = Mock()
        task.task_id = 1
        task.exam = Mock()
        task.exam.tasks_link = "http://invalid.url"

        mock_get.side_effect = Exception("Connection error")

        MatriculationTaskService.populate_task_content(task)
        assert "error while processing pdf" in task.content.lower()

    def test_single_page(self):
        assert MatriculationTaskService._parse_pages_string("5") == [5]

    def test_page_range(self):
        assert MatriculationTaskService._parse_pages_string("2-4") == [2, 3, 4]

    def test_empty_string(self):
        assert MatriculationTaskService._parse_pages_string("") == []

    def test_invalid_input(self):
        assert MatriculationTaskService._parse_pages_string("abc") == []
        assert MatriculationTaskService._parse_pages_string(None) == []

    @patch("services.fitz.open")
    def test_successful_pdf_extraction(self, mock_open):
        mock_exam = MagicMock()
        mock_exam.page_count = 3
        mock_open.return_value.__enter__.return_value = mock_exam

        mock_task_doc = MagicMock()
        mock_open.side_effect = [mock_task_doc, mock_exam]

        result = MatriculationTaskService.get_single_task_pdf("fake.pdf", [1, 2])
        assert result is not None
        mock_task_doc.insert_pdf.assert_called()

    def test_file_not_found(self):
        result = MatriculationTaskService.get_single_task_pdf("notfound.pdf", [1])
        assert result is None

    @patch("services.Exam.objects.annotate")
    def test_queryset_filtering(self, mock_annotate):
        mock_annotate.return_value.filter.return_value = "filtered_qs"

        result = MatriculationTaskService.get_exams_with_available_tasks()
        assert result == "filtered_qs"
        mock_annotate.assert_called()
