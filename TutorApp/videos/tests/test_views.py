from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from users.factories import TeacherFactory, UserFactory
from videos.factories import VideoFactory

from TutorApp.videos.models import Video


class VideoCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("video_form")
        self.password = "testpass123"
        self.teacher = TeacherFactory(password=self.password)
        self.student = UserFactory(password=self.password)

    @patch("videos.views.UserService")
    def test_teacher_can_access_video_form(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "videos/video_form.html")

    @patch("videos.views.UserService")
    def test_student_cannot_access_video_form(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = False
        self.client.login(username=self.student.username, password=self.password)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    @patch("videos.views.UserService")
    def test_valid_video_form_submission_creates_video(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        data = {
            "title": "Test Video",
            "youtube_url": "https://youtube.com/watch?v=xyz123",
            "type": 4,
            "subcategory": "Mathematical functions",
            "level": "2",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Video.objects.count(), 1)
        video = Video.objects.first()
        self.assertEqual(video.title, "Test Video")
        self.assertEqual(video.level, "2")

    @patch("videos.views.UserService")
    def test_invalid_video_form_returns_errors(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        invalid_data = {
            "title": "",
            "youtube_url": "not-a-valid-url",
            "type": "",
            "subcategory": "",
            "level": "",
        }

        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "title", "To pole jest wymagane.")
        self.assertEqual(Video.objects.count(), 0)

    @patch("videos.views.UserService")
    def test_student_cannot_submit_video_form(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = False
        self.client.login(username=self.student.username, password=self.password)

        data = {
            "title": "Should Not Work",
            "youtube_url": "https://youtube.com/watch?v=fail",
            "type": 1,
            "subcategory": "Denied",
            "level": "1",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Video.objects.count(), 0)

    def test_unauthenticated_user_cannot_post_video(self):
        data = {
            "title": "No Auth",
            "youtube_url": "https://youtube.com/watch?v=fail",
            "type": 1,
            "subcategory": "None",
            "level": "1",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))
        self.assertEqual(Video.objects.count(), 0)

    @patch("videos.views.UserService")
    def test_malformed_timestamps_are_ignored(self, mock_user_service):
        mock_user_service.return_value.is_teacher.return_value = True
        self.client.login(username=self.teacher.username, password=self.password)

        data = {
            "title": "Video with Bad Timestamps",
            "youtube_url": "https://youtube.com/watch?v=test",
            "type": 1,
            "subcategory": "Errors",
            "level": "1",
            "timestamp_block": "wrongformat\nanother bad line\n01:23 Good Label",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        video = Video.objects.first()
        self.assertIsNotNone(video)
        self.assertEqual(video.videotimestamp_set.count(), 1)
        self.assertEqual(video.videotimestamp_set.first().label, "Good Label")


class SectionListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("videos:section_list")
        VideoFactory.create_batch(3, type=1)
        VideoFactory.create_batch(2, type=2)

    def test_response_status_and_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "videos/section_list.html")

    def test_context_contains_section_data(self):
        response = self.client.get(self.url)
        sections = response.context["sections"]
        self.assertEqual(len(sections), 2)
        self.assertIn("video_count", sections[0])
        self.assertIn("type", sections[0])

    def test_section_labels_in_context(self):
        response = self.client.get(self.url)
        self.assertIn("section_labels", response.context)
        self.assertIsInstance(response.context["section_labels"], dict)


class SubcategoryListViewTests(TestCase):
    def setUp(self):
        self.section_id = 4
        self.url = reverse("videos:subcategory_list", args=[self.section_id])
        VideoFactory.create_batch(2, type=self.section_id, subcategory="Intro")
        VideoFactory.create_batch(1, type=self.section_id, subcategory="Advanced")

    def test_response_status_and_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "videos/subcategory_list.html")

    def test_context_contains_subcategories(self):
        response = self.client.get(self.url)
        subcategories = response.context["subcategories"]
        self.assertEqual(len(subcategories), 2)
        self.assertIn("video_count", subcategories[0])
        self.assertIn("subcategory", subcategories[0])

    def test_section_metadata_in_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["section_id"], self.section_id)
        self.assertEqual(
            response.context["section_name"], dict(Video.section)[self.section_id]
        )


class VideoListViewTests(TestCase):
    def setUp(self):
        self.section_id = 5
        self.subcategory = "Basics"
        self.url = reverse(
            "videos:video_list", args=[self.section_id, self.subcategory]
        )
        VideoFactory.create_batch(3, type=self.section_id, subcategory=self.subcategory)
        VideoFactory.create_batch(1, type=self.section_id, subcategory="Other")

    def test_response_status_and_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "videos/video_list.html")

    def test_queryset_filters_correctly(self):
        response = self.client.get(self.url)
        videos = response.context["videos"]
        self.assertEqual(len(videos), 3)
        self.assertTrue(
            all(
                v.type == self.section_id and v.subcategory == self.subcategory
                for v in videos
            )
        )

    def test_context_contains_expected_keys(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.context["section_name"], dict(Video.section)[self.section_id]
        )
        self.assertEqual(response.context["subcategory"], self.subcategory)

    def test_video_list_view_empty_for_nonexistent_combination(self):
        nonexistent_section_id = 999
        nonexistent_subcategory = "NonexistentSubcategory"
        url = reverse(
            "videos:video_list", args=[nonexistent_section_id, nonexistent_subcategory]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["videos"], [])
