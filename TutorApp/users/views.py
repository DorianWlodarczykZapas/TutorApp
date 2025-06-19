from datetime import timedelta
from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, View

from ..plans.models import Plan, UserPlan
from .forms import LoginForm, UserRegisterForm
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


class LoginView(View):
    template_name: str = "login.html"
    form_class = LoginForm

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(self.get_success_url(request))
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(self.get_success_url(request, user))
            messages.error(request, _("Invalid username or password."))

        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        logout(request)
        return redirect("login")
