from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    SCHOOL_TYPE_CHOICES = [
        ("PRIMARY", _("Primary School")),
        ("SECONDARY", _("Secondary School")),
    ]

    school_type = models.CharField(
        max_length=10, choices=SCHOOL_TYPE_CHOICES, null=True, blank=True
    )
    role = [(1, "Student"), (2, "Teacher"), (3, "Admin")]
    role_type = models.IntegerField(choices=role, default=1)
