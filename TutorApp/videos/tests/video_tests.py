from datetime import timedelta
from unittest.mock import patch

from courses.choices import SubjectChoices
from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory

from .videos.models import Video, VideoTimestamp


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
            "step_1-level": 3,
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
