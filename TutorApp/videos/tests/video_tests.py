from datetime import timedelta
from unittest.mock import Mock, patch

from courses.choices import SubjectChoices
from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory
from videos.models import Video, VideoTimestamp


class AddVideoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("videos:add_video")
        self.student = UserFactory.create()
        self.teacher = TeacherFactory.create()
        self.section = SectionFactory.create()
        self.step_1_data = {
            "video_create_wizard-current_step": "step_1",
            "step_1-youtube_url": "https://www.youtube.com/watch?v=xxxxx",
            "step_1-subject": SubjectChoices.MATH,
            "step_1-level": 2,
            "step_1-section": self.section.pk,
        }
        self.step_2_data = {
            "video_create_wizard-current_step": "step_2",
            "step_2-title": "Test Video",
            "timestamps-TOTAL_FORMS": "1",
            "timestamps-INITIAL_FORMS": "1",
            "timestamps-MIN_NUM_FORMS": "0",
            "timestamps-MAX_NUM_FORMS": "1000",
            "timestamps-0-label": "Introduction",
            "timestamps-0-start_time": "00:00:10",
            "timestamps-0-timestamp_type": 4,
        }

        self.mock_service_data = {
            "title": "Test Video Title",
            "description": "Test Video Description",
        }

        self.mock_timestamps = [
            {
                "label": "Introduction",
                "start_time": timedelta(seconds=10),
                "timestamp_type": VideoTimestamp.TimestampType.MATRICULATION_BASIC,
            }
        ]

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
        self.assertEqual(response.status_code, 403)

    def test_teacher_can_add_video(self):
        """Test case that checks if teacher can add video"""
        self.client.force_login(self.teacher)

        with patch("videos.views.video_views.YoutubeService") as MockService:
            instance = MockService.return_value
            instance.extract_video_title_and_description.return_value = (
                self.mock_service_data
            )
            instance.parse_timestamps.return_value = self.mock_timestamps

            response = self.client.post(self.url, self.step_1_data)
            print(response.context["form"].errors)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Video.objects.exists())

            response = self.client.post(self.url, self.step_2_data)
            self.assertRedirects(response, reverse("videos:video_list"))

            video = Video.objects.get(title="Test Video")
            self.assertEqual(video.youtube_url, "https://www.youtube.com/watch?v=xxxxx")
            self.assertEqual(video.section, self.section)

            timestamp = VideoTimestamp.objects.get(video=video)
            self.assertEqual(timestamp.label, "Introduction")
            self.assertEqual(timestamp.start_time, timedelta(seconds=10))

    def test_invalid_youtube_url(self):
        """Test case that contains invalid youtube url"""
        self.client.force_login(self.teacher)
        invalid_step_1 = {
            **self.step_1_data,
            "step_1-youtube_url": "xyz",
        }

        response = self.client.post(self.url, invalid_step_1)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Video.objects.exists())
        form = response.context["form"]
        self.assertFormError(form, "youtube_url", "Enter a valid URL.")

    def test_missing_title(self):
        """Test case that contains missing title"""

        self.client.force_login(self.teacher)

        invalid_step_2 = {
            **self.step_2_data,
            "step_2-title": "",
        }

        with patch("videos.views.video_views.YoutubeService") as MockService:
            instance = MockService.return_value
            instance.extract_video_title_and_description.return_value = (
                self.mock_service_data
            )
            instance.parse_timestamps.return_value = self.mock_timestamps

            response = self.client.post(self.url, self.step_1_data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Video.objects.exists())

            response = self.client.post(self.url, invalid_step_2)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Video.objects.exists())
            form = response.context["form"]
            self.assertFormError(form, "title", "This field is required.")

    def test_invalid_timestamp_data(self):
        """Test case that checks with invalid timestamp data"""
        self.client.force_login(self.teacher)

        invalid_step_2 = {
            **self.step_2_data,
            "timestamps-0-label": "",
        }

        with patch("videos.views.video_views.YoutubeService") as MockService:
            instance = MockService.return_value
            instance.extract_video_title_and_description.return_value = (
                self.mock_service_data
            )
            instance.parse_timestamps.return_value = self.mock_timestamps

            response = self.client.post(self.url, self.step_1_data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Video.objects.exists())

            response = self.client.post(self.url, invalid_step_2)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse("videos:add_video"))
            self.assertFalse(Video.objects.exists())
            messages = list(response.wsgi_request._messages)
            self.assertEqual(
                str(messages[0]), "Invalid timestamp data. Please check your changes."
            )

    def test_missing_section(self):
        """Test case that contains missing section"""

        self.client.force_login(self.teacher)

        invalid_step_1 = {
            **self.step_1_data,
            "step_1-section": "",
        }

        response = self.client.post(self.url, invalid_step_1)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Video.objects.exists())
        form = response.context["form"]
        self.assertFormError(form, "section", "This field is required.")

    def test_student_cannot_post(self):
        """Test to verify a student's attempt to submit a form"""

        self.client.force_login(self.student)

        response = self.client.post(self.url, self.step_1_data)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Video.objects.exists())

    def test_process_step_saves_youtube_data_to_step_2_form(self):
        """Test case that checks if process_step correctly passes YouTube
        service data (title, timestamps) into the step_2 form/formset"""

        self.client.force_login(self.teacher)

        with patch("videos.views.video_views.YoutubeService") as MockService:
            instance = MockService.return_value
            instance.extract_video_title_and_description.return_value = (
                self.mock_service_data
            )
            instance.parse_timestamps.return_value = self.mock_timestamps

            response = self.client.post(self.url, self.step_1_data)

            response = self.client.post(self.url, self.step_1_data)
            print(list(response.context.keys()))
            print(response.context.get("wizard", {}))

            self.assertEqual(response.status_code, 200)

            self.assertEqual(
                response.context["form"].initial["title"],
                self.mock_service_data["title"],
            )

            expected_timestamp_initial = {
                "label": "Introduction",
                "start_time": VideoTimestamp.format_duration(timedelta(seconds=10)),
                "timestamp_type": int(VideoTimestamp.TimestampType.MATRICULATION_BASIC),
            }

            formset = response.context["formset"]
            self.assertEqual(formset[0].initial, expected_timestamp_initial)

    def test_transaction_rollback_on_timestamp_creation_error(self):
        """Test case that checks if Video creation is rolled back when
        an error occurs while creating one of its VideoTimestamps"""

        self.client.force_login(self.teacher)

        two_timestamps_data = {
            **self.step_2_data,
            "timestamps-TOTAL_FORMS": "2",
            "timestamps-1-label": "Functions",
            "timestamps-1-start_time": "00:02:30",
            "timestamps-1-timestamp_type": 4,
        }

        with patch("videos.views.video_views.YoutubeService") as MockService:
            instance = MockService.return_value
            instance.extract_video_title_and_description.return_value = (
                self.mock_service_data
            )
            instance.parse_timestamps.return_value = self.mock_timestamps

            response = self.client.post(self.url, self.step_1_data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Video.objects.exists())

            with patch(
                "videos.views.video_views.VideoTimestamp.objects.create"
            ) as mock_create:
                mock_create.side_effect = [
                    Mock(),
                    Exception("wrong timestamp data"),
                ]

                with self.assertRaises(Exception):
                    self.client.post(self.url, two_timestamps_data)

            self.assertFalse(Video.objects.exists())
            self.assertFalse(VideoTimestamp.objects.exists())

    def test_multiple_timestamps_are_created(self):
        """Test case that checks if all timestamps from the formset
        are correctly saved to the database, not just the first one"""

        self.client.force_login(self.teacher)

        three_timestamp_data = {
            **self.step_2_data,
            "timestamps-TOTAL_FORMS": "3",
            "timestamps-1-label": "Functions",
            "timestamps-1-start_time": "00:02:30",
            "timestamps-1-timestamp_type": 4,
            "timestamps-2-label": "Equations",
            "timestamps-2-start_time": "00:03:30",
            "timestamps-2-timestamp_type": 2,
        }

        with patch("videos.views.video_views.YoutubeService") as MockService:
            instance = MockService.return_value
            instance.extract_video_title_and_description.return_value = (
                self.mock_service_data
            )
            instance.parse_timestamps.return_value = self.mock_timestamps

            response = self.client.post(self.url, self.step_1_data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Video.objects.exists())

            response = self.client.post(self.url, three_timestamp_data)
            self.assertRedirects(response, reverse("videos:video_list"))

            self.assertEqual(VideoTimestamp.objects.count(), 3)
            self.assertTrue(Video.objects.exists())

            video = Video.objects.get(title="Test Video")
            timestamps = VideoTimestamp.objects.filter(video=video).order_by("label")

            self.assertEqual(timestamps[0].label, "Equations")
            self.assertEqual(timestamps[0].start_time, timedelta(minutes=3, seconds=30))
            self.assertEqual(timestamps[0].timestamp_type, 2)
            self.assertEqual(timestamps[1].label, "Functions")
            self.assertEqual(timestamps[1].start_time, timedelta(minutes=2, seconds=30))
            self.assertEqual(timestamps[1].timestamp_type, 4)
            self.assertEqual(timestamps[2].label, "Introduction")
            self.assertEqual(timestamps[2].start_time, timedelta(minutes=0, seconds=10))
            self.assertEqual(timestamps[2].timestamp_type, 4)
