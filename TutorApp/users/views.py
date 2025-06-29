from typing import Any

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, View

from .forms import LoginForm, UserRegisterForm
from .models import User
from .services import UserService


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form: UserRegisterForm) -> HttpResponse:
        service = UserService()
        service.register_user(form)
        messages.success(self.request, "Account has been created. You can now log in.")
        return super().form_valid(form)

    def form_invalid(self, form: UserRegisterForm) -> HttpResponse:
        messages.error(
            self.request,
            "There was an error creating your account. Please correct the form below.",
        )
        return super().form_invalid(form)


class LoginView(View):
    template_name: str = "users/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("users:home")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return render(request, self.template_name, {"form": self.form_class()})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            service = UserService()
            user = service.login_user(request, username, password)

            if user:
                messages.success(request, _("You have been successfully logged in."))
                return redirect(self.success_url)

            messages.error(request, _("Invalid username or password."))

        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        logout(request)
        return redirect("login")


class HomeView(LoginRequiredMixin, TemplateView):
    template_name: str = "home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Home")
        return context
