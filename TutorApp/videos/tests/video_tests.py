from courses.choices import SubjectChoices
from courses.tests.factories import SectionFactory
from django.test import Client, TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory


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
