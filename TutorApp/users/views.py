from datetime import timedelta
from typing import Any

from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from ..plans.models import Plan, UserPlan
from .forms import UserRegisterForm
from .models import User


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form: UserRegisterForm) -> Any:
        user: User = form.save(commit=False)
        user.role_type = 1
        user.save()
        self.assign_trial_plan(user)
        return super().form_valid(form)

    def assign_trial_plan(self, user: User) -> None:
        try:
            trial_plan = Plan.objects.get(type=Plan.PlanType.TRIAL)
        except Plan.DoesNotExist:
            return

        today = timezone.now().date()
        UserPlan.objects.create(
            user=user,
            plan=trial_plan,
            start_date=today,
            valid_to=today + timedelta(days=7),
            is_trial=True,
            trial_days=7,
        )
