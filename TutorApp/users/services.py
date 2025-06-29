from datetime import timedelta
from typing import Optional

from django.contrib.auth import authenticate, login
from django.http import HttpRequest
from django.utils import timezone
from plans.models import Plan, UserPlan
from users.forms import UserRegisterForm
from users.models import User


class UserService:
    def __init__(self, user: Optional[User] = None):
        self.user = user

    def register_user(self, form: UserRegisterForm, default_role_type: int = 1) -> User:
        """Create and save a user from a registration form and assign a trial plan."""
        user = form.save(commit=False)
        user.role_type = default_role_type
        user.save()
        self.user = user
        self.assign_trial_plan()
        return user

    def is_teacher(self) -> bool:
        """Check if the user is authenticated and has a teacher role."""
        return self.user and self.user.is_authenticated and self.user.role_type == 2

    def is_student(self) -> bool:
        """Check if the user is authenticated and has a student role."""
        return self.user and self.user.is_authenticated and self.user.role_type == 1

    def is_admin(self) -> bool:
        """Check if the user is authenticated and has an admin role."""
        return self.user and self.user.is_authenticated and self.user.role_type == 3

    def assign_trial_plan(self) -> bool:
        """Assign a trial plan to the user if not already assigned. Returns True if successful."""
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
    ) -> Optional[User]:
        """
        Authenticate and log in the user. Returns the User if successful, otherwise None.
        """
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            self.user = user
            return user
        return None
