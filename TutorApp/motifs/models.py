from django.db import models

from ..examination_tasks.choices import SubjectChoices
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
        Section, on_delete=models.CASCADE, related_name="topics", verbose_name="Section"
    )
    content = models.CharField(
        max_length=255,
    )
    answer = models.CharField()
    answer_picture = models.ImageField(
        upload_to="motifs/subject/section/",
        blank=True,
        null=True,
    )
    is_in_matriculation_sheets = models.BooleanField(
        default=False,
    )
