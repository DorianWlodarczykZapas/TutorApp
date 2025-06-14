from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Plan(models.Model):
    class PlanType(models.IntegerChoices):
        BASE = 1, _("Base")
        PREMIUM = 2, _("Premium")
        TRIAL = 3, _("Trial")

    name = models.CharField(max_length=255)
    type = models.IntegerField(choices=PlanType.choices, default=PlanType.BASE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period = models.CharField(max_length=50)
    max_projects = models.IntegerField()
    max_rooms_per_project = models.IntegerField()
    advanced_features_enabled = models.BooleanField(default=False)
    trial_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserPlan(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)
    last_payment_date = models.DateField(null=True, blank=True)
    next_payment_date = models.DateField(null=True, blank=True)
    is_trial = models.BooleanField(default=False)
    trial_days = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

