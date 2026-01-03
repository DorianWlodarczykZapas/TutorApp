from django.db import models

from ..examination_tasks.choices import LEVEL_CHOICES, SubjectChoices
from ..examination_tasks.models import Section


def motif_image_path(instance, filename) -> str:
    """
    Method that returns the path of the motif image

    Args:
    instance: instance of the model
    filename: filename of the motif image
    Returns:
        Path of the motif image
    """
    return f"motifs/{instance.subject}/{instance.section.id}/{filename}"


class Motif(models.Model):
    subject = models.CharField(
        max_length=10, choices=SubjectChoices, verbose_name="Subject", default=1
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="motifs", verbose_name="Section"
    )
    level_type = models.IntegerField(
        choices=LEVEL_CHOICES,
        null=True,
        blank=True,
        help_text="Motif level: basic or extended (Matriculation only)",
    )

    content = models.CharField(
        max_length=255,
        verbose_name="Motif content",
        help_text="Whole motif content",
    )

    answer = models.TextField(
        verbose_name="answer",
        help_text="Explanation about chosen motif",
    )
    answer_picture = models.ImageField(
        upload_to=motif_image_path,
        blank=True,
        null=True,
        help_text="Motif explanation picture if needed",
    )
    is_in_matriculation_sheets = models.BooleanField(
        default=False,
        verbose_name="If exists in matriculation sheets",
    )

    is_mandatory = models.BooleanField(
        default=True,
        verbose_name="Mandatory for students",
        help_text="Whether students must learn this motif",
    )

    class Meta:
        verbose_name = "Motif in subject"
        verbose_name_plural = "Motifs in subject"
        ordering = ["subject", "section", "level_type"]

    def __str__(self):
        level = self.get_level_type_display() if self.level_type else "No Level"
        return f"{self.get_subject_display()} - {self.section.name} - {level}: {self.content[:50]}"
