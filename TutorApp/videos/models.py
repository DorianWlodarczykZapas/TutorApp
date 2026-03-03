import re

from courses.models import Section
from django.db import models
from django.utils.translation import gettext_lazy as _
from examination_tasks.choices import SchoolLevelChoices, SubjectChoices


class Video(models.Model):
    title = models.CharField(max_length=255)
    youtube_url = models.URLField()
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="videos"
    )

    @property
    def youtube_video_id(self):
        """Converts video url to format available to set video in application"""
        match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", self.youtube_url)
        return match.group(1) if match else ""

    subject = models.IntegerField(
        choices=SubjectChoices.choices, verbose_name=_("Subject")
    )

    level = models.IntegerField(
        choices=SchoolLevelChoices.choices, verbose_name=_("School Level")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} – {self.get_level_display()}"


class VideoTimestamp(models.Model):
    class TimestampType(models.IntegerChoices):
        EXERCISE = 1, _("Exercise")
        TASK = 2, _("Task")

    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="timestamps"
    )
    label = models.CharField(max_length=255)
    start_time = models.DurationField(help_text=_("Format: HH:MM:SS"))
    timestamp_type = models.IntegerField(choices=TimestampType.choices)

    @property
    def start_seconds(self):
        """Method that helps use timestamp with youtube api"""
        return int(self.start_time.total_seconds())

    @property
    def start_time_display(self):
        total = int(self.start_time.total_seconds())
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def __str__(self):
        return f"{self.video.title} – {self.label}"

    class Meta:
        ordering = ["start_time"]
        verbose_name = _("Video Timestamp")
        verbose_name_plural = _("Video Timestamps")
