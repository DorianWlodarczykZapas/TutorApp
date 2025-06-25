from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from users.tests.factories import UserFactory

User = get_user_model()


class UserRegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse("register")

    def test_register_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_register_view_post_valid(self):
        data = {
            "username": "newuser",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "email": "newuser@example.com",
            "school_type": "SECONDARY",
        }
        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse("login"))
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.role_type, 1)

    def test_register_view_post_invalid(self):
        data = {
            "username": "newuser",
            "password1": "weak",
            "password2": "notmatching",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, "form", "password2", "The two password fields didn’t match."
        )
        self.assertEqual(User.objects.count(), 0)


class LoginViewTests(TestCase):
    def setUp(self):
        self.url = reverse("login")
        self.password = "StrongPassword123!"
        self.user = UserFactory(password=self.password)

    def test_login_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
