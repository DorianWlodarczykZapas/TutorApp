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

    subject = models.IntegerField(
        choices=SubjectChoices.choices, verbose_name=_("Subject")
    )

    class VideoLevel(models.TextChoices):
        PRIMARY = "1", _("Primary School")
        SECONDARY = "2", _("Secondary School")

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

    def __str__(self):
        return f"{self.video.title} – {self.label}"

    class Meta:
        ordering = ["start_time"]
        verbose_name = _("Video Timestamp")
        verbose_name_plural = _("Video Timestamps")
