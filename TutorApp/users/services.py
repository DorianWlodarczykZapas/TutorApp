from datetime import timedelta
from typing import Optional

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from django.utils import timezone
from models import User
from plans.models import Plan, UserPlan


class UserService:
    def __init__(self, user: Optional["User"] = None):
        self.user = user

    def register_user(self, form, default_role_type: int = 1):
        """Create and save a user from a registration form and assign a trial plan."""

        user: User = form.save(commit=False)
        user.role_type = default_role_type
        user.save()
        self.user = user
        self.assign_trial_plan()
        return user

    def is_teacher(self) -> bool:
        return (
            self.user
            and self.user.is_authenticated
            and getattr(self.user, "role_type", None) == 2
        )

    def is_student(self) -> bool:
        return (
            self.user
            and self.user.is_authenticated
            and getattr(self.user, "role_type", None) == 1
        )

    def is_admin(self) -> bool:
        return (
            self.user
            and self.user.is_authenticated
            and getattr(self.user, "role_type", None) == 3
        )

    def assign_trial_plan(self) -> bool:
        if not self.user or not self.user.is_authenticated:
            return False

        if UserPlan.objects.filter(user=self.user).exists():
            return False

        plan = Plan.objects.filter(type=Plan.PlanType.TRIAL).first()
        if not plan:
            return False

        today = timezone.now().date()
        UserPlan.objects.create(
            user=self.user,
            plan=plan,
            start_date=today,
            valid_to=today + timedelta(days=plan.trial_days),
            is_trial=True,
            trial_days=plan.trial_days,
        )
        return True

    def login_user(
        self, request: HttpRequest, username: str, password: str
    ) -> Optional["User"]:

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            self.user = user
            return user
        return None

    def logout_user(self, request: HttpRequest) -> None:
        logout(request)
        self.user = None
