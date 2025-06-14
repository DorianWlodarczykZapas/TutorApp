from django.db import models
from django.utils.translation import gettext_lazy as _




class Video(models.Model):
    title = models.CharField(max_length=255)
    youtube_url = models.URLField()
    section = (
        (1, "Real numbers"),
        (2, "Language of mathematics"),
        (3, "Systems of equations"),
        (4, "Functions"),
        (5, "Linear function"),
        (6, "Planimetry"),
        (7, "Quadratic function"),
        (8, "Polynomials"),
        (9, "Measurable function"),
        (10, "Trigonometry"),
        (11, "Planimetry circles"),
        (12, "Exponential and logarithmic functions"),
        (13, "Trigonometric functions"),
        (14, "Analytical geometry"),
        (15, "Sequences"),
        (16, "Differential calculus"),
        (17, "Statistics"),
        (18, "Probability"),
        (19, "Stereometry"),
    )
    type = models.IntegerField(choices=section)


    subcategory = models.CharField(max_length=255)


    class VideoLevel(models.TextChoices):
        PRIMARY = 1, _('Primary School')
        SECONDARY = 2, _('Secondary School')

    level = models.CharField(max_length=10, choices=VideoLevel.choices)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} – {self.get_level_display()}"


class VideoTimestamp(models.Model):
    class TimestampType(models.TextChoices):
        EXERCISE = 1, _('Exercise')
        TASK = 2, _('Task')

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='timestamps')
    label = models.CharField(max_length=255)
    start_time = models.DurationField(help_text=_("Format: HH:MM:SS"))
    type = models.CharField(max_length=10, choices=TimestampType.choices)

    def __str__(self):
        return f"{self.video.title} – {self.label}"
