from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Plan(models.Model):
    class PlanType(models.IntegerChoices):
        BASE = 1, _("Base")
        PREMIUM = 2, _("Premium")
        TRIAL = 3, _("Trial")
        ULTIMATE = 4, _("Ultimate")

    name = models.CharField(max_length=255)
    type = models.IntegerField(choices=PlanType.choices, default=PlanType.BASE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="pln")
    billing_period = models.CharField(max_length=50)
    advanced_features_enabled = models.BooleanField(default=False)
    trial_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_price_id = models.CharField(max_length=255, null=True, blank=True)

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
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)

    @property
    def is_premium_or_trial(self):
        return self.is_active and self.plan.type in [
            Plan.PlanType.PREMIUM,
            Plan.PlanType.TRIAL,
        ]

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
