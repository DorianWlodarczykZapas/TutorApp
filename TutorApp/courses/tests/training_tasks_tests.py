from courses.filters import TrainingTaskFilter
from courses.models import TrainingTask
from courses.tests.factories import BookFactory, SectionFactory, TrainingTaskFactory
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext as _
from users.factories import TeacherFactory, UserFactory
from videos.tests.factories import VideoTimestampFactory


class AddTrainingTasksTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.url = reverse("add_training_tasks")
        self.section = SectionFactory.create()
        self.book = BookFactory.create()
        self.page_number = 25
        self.timestamp = VideoTimestampFactory.create()
        self.valid_data = {
            "task_content": "Solve this equation",
            "answer": "4",
            "level": 3,
            "section": self.section.pk,
            "book": self.book.pk,
            "page_number": self.page_number,
            "explanation_timestamp": self.timestamp.pk,
        }

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_can_teacher_access(self):
        """
        Test case that checks if teacher can access adding topic page
        """
        self.client.force_login(self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_can_student_access(self):
        """Test case that checks if student can access adding topic page"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_add_training_task(self):
        """Test case that adds training task"""
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            TrainingTask.objects.filter(task_content="Solve this equation").exists()
        )

    def test_add_training_task_with_empty_content(self):
        """Test case that adds training task with empty content"""
        self.valid_data["task_content"] = ""
        self.client.force_login(self.teacher)
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_empty_answer(self):
        """Test case that adds training task with empty answer"""
        self.valid_data["answer"] = ""
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_invalid_level(self):
        """Test case that adds training task with invalid level"""
        self.valid_data["level"] = 99
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_wrong_level_type(self):
        """Test case that adds training task with wrong level type"""
        self.valid_data["level"] = "a"
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_invalid_section(self):
        """Test case that adds training task with invalid section"""
        self.valid_data["section"] = 99999
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_without_section(self):
        """Test case that adds training task without section"""
        self.valid_data["section"] = ""
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 1)

    def test_add_training_task_with_level_zero(self):
        """Test case that adds training task with level 0"""
        self.valid_data["level"] = 0
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_negative_level(self):
        """Test case that adds training task with negative level"""
        self.valid_data["level"] = -1
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_answer_too_long(self):
        """Test case that adds training task with answer exceeding max_length"""
        self.valid_data["answer"] = "x" * 256
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)

    def test_add_training_task_with_page_number_without_book(self):
        """Test case that adds training task with page number but without book"""
        self.valid_data["book"] = ""
        self.client.force_login(self.teacher)
        self.client.post(self.url, data=self.valid_data)
        self.assertEqual(TrainingTask.objects.count(), 0)


class TrainingTaskListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("training_tasks_list")
        self.student = UserFactory.create(grade=1)
        self.book = BookFactory.create(grade=1)
        self.section = SectionFactory.create(book=self.book)
        self.task = TrainingTaskFactory.create(section=self.section)

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_access_page(self):
        """Test case that checks if access is working"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_completion_percentage_is_zero_when_no_tasks(self):
        """Test case about 0% progress"""
        self.task.delete()
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["completion_percentage"], 0)

    def test_completion_percentage_when_task_completed(self):
        """Test case about 100% progress"""
        self.task.completed_by.add(self.student)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["completion_percentage"], 100)

    def test_completion_percentage_partial(self):
        """Test case about 50% progress"""
        TrainingTaskFactory.create(section=self.section)
        self.task.completed_by.add(self.student)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["completion_percentage"], 50)

    def test_context_has_title(self):
        """Test case about context title"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["title"], _("Training Tasks"))

    def test_context_has_total_tasks(self):
        """Test case about total tasks value"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["total_tasks"], 1)

    def test_context_has_completed_tasks(self):
        """Test case about completed tasks value"""
        self.task.completed_by.add(self.student)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["completed_tasks"], 1)

    def test_context_total_tasks_multiple(self):
        """Test case about multiple training tasks"""
        TrainingTaskFactory.create_batch(5, section=self.section)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["total_tasks"], 6)

    def test_completion_percentage_with_multiple_tasks(self):
        """Testing when 1/5 tasks are completed"""
        TrainingTaskFactory.create_batch(4, section=self.section)
        self.task.completed_by.add(self.student)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["completion_percentage"], 20)

    def test_queryset_returns_correct_tasks(self):
        """Test case where queryset returns all objects"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["tasks"].count(), 1)

    def test_queryset_returns_all_tasks(self):
        """Test case where queryset returns all objects(multiple tasks)"""
        TrainingTaskFactory.create_batch(4, section=self.section)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["tasks"].count(), 5)

    def test_queryset_filters_by_user_grade(self):
        """Test case where book has different grade"""
        other_book = BookFactory.create(grade=2)
        other_section = SectionFactory.create(book=other_book)
        TrainingTaskFactory.create(section=other_section)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["tasks"].count(), 1)


class TrainingTaskFilterTests(TestCase):
    def setUp(self):
        self.student = UserFactory.create(grade=1)
        self.book = BookFactory.create(grade=1)
        self.section = SectionFactory.create(book=self.book)
        self.uncompleted_task = TrainingTaskFactory.create(section=self.section)
        self.completed_task = TrainingTaskFactory.create(section=self.section)
        self.completed_task.completed_by.add(self.student)

    def test_filter_completed_tasks(self):
        """Test case that filters completed tasks"""
        filterset = TrainingTaskFilter(
            data={"completed": "completed"},
            queryset=TrainingTask.objects.all(),
            user=self.student,
        )

        self.assertEqual(filterset.qs.count(), 1)
        self.assertIn(self.completed_task, filterset.qs)

    def test_filter_uncompleted_tasks(self):
        """Test case that filters uncompleted tasks"""
        filterset = TrainingTaskFilter(
            data={"completed": "uncompleted"},
            queryset=TrainingTask.objects.all(),
            user=self.student,
        )
        self.assertEqual(filterset.qs.count(), 1)
        self.assertIn(self.uncompleted_task, filterset.qs)

    def test_filter_completed_without_user(self):
        """Test case about no user passed filter"""
        filterset = TrainingTaskFilter(
            data={"completed": "completed"},
            queryset=TrainingTask.objects.all(),
            user=None,
        )
        self.assertEqual(filterset.qs.count(), TrainingTask.objects.count())

    def test_qs_filters_by_grade_when_no_data(self):
        """Test case about filter by grade with no data"""
        other_book = BookFactory.create(grade=2)
        other_section = SectionFactory.create(book=other_book)
        TrainingTaskFactory.create(section=other_section)

        filterset = TrainingTaskFilter(
            data=None, queryset=TrainingTask.objects.all(), user=self.student
        )
        self.assertEqual(filterset.qs.count(), 2)

    def test_qs_does_not_filter_by_grade_when_data_provided(self):
        """Test case when data is passed but not filtered by grade"""
        other_book = BookFactory.create(grade=2)
        other_section = SectionFactory.create(book=other_book)
        TrainingTaskFactory.create(section=other_section)

        filterset = TrainingTaskFilter(
            data={"completed": ""},
            queryset=TrainingTask.objects.all(),
            user=self.student,
        )
        self.assertEqual(filterset.qs.count(), 3)

    def test_book_queryset_filtered_by_user_grade(self):
        """Test case where book filter shows books same as user's grade"""
        other_book = BookFactory.create(grade=2)

        filterset = TrainingTaskFilter(
            data=None, queryset=TrainingTask.objects.all(), user=self.student
        )

        book_queryset = filterset.filters["book"].queryset
        self.assertIn(self.book, book_queryset)
        self.assertNotIn(other_book, book_queryset)

    def test_section_queryset_filtered_by_user_grade(self):
        """Test case where section filter shows sections same as user's grade"""
        other_book = BookFactory.create(grade=2)
        other_section = SectionFactory.create(book=other_book)

        filterset = TrainingTaskFilter(
            data=None, queryset=TrainingTask.objects.all(), user=self.student
        )

        section_queryset = filterset.filters["section"].queryset
        self.assertIn(self.section, section_queryset)
        self.assertNotIn(other_section, section_queryset)


class TrainingTaskDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = UserFactory.create(grade=1)
        self.book = BookFactory.create(grade=1)
        self.section = SectionFactory.create(book=self.book)
        self.task = TrainingTaskFactory.create(section=self.section)
        self.url = reverse("training_tasks_detail", kwargs={"pk": self.task.pk})

    def test_unauthorized_access(self):
        """Test case that checks if unauthorized access is working"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_access_page(self):
        """Test case that checks if access is working"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_is_completed_false(self):
        """Test case that checks if task is not completed"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["is_completed"], False)

    def test_context_is_completed_true(self):
        """Test case that checks if task is completed"""
        self.task.completed_by.add(self.student)
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["is_completed"], True)

    def test_task_not_found(self):
        """Test case that checks if task not found returns 404"""
        url = reverse("training_tasks_detail", kwargs={"pk": 99999})
        self.client.force_login(self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_context_has_title(self):
        """Test case that checks if title is in context"""
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.context["title"], _("Task Details"))
