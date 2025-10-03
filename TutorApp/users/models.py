from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    SCHOOL_TYPE_CHOICES = [
        (1, _("Primary School")),
        (2, _("Secondary School")),
    ]

    school_type = models.IntegerField(
        max_length=20, choices=SCHOOL_TYPE_CHOICES, null=True, blank=True
    )
    role = [(1, "Student"), (2, "Teacher"), (3, "Admin")]
    role_type = models.IntegerField(choices=role, default=1)
    GRADE_TYPE_CHOICES = [
        (1, _("7th Grade of Primary School")),
        (2, _("8th Grade of Primary School")),
        (3, _("1st Year of Secondary School")),
        (4, _("2nd Year of Secondary School")),
        (5, _("3rd Year of Secondary School")),
        (6, _("4th Year of Secondary School")),
    ]
    grade_type = models.IntegerField(
        max_length=20, choices=GRADE_TYPE_CHOICES, null=True, blank=True
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.username} - {self.role} - {self.grade_type}"
