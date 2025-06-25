from django.test import TestCase
from django.urls import reverse


class UserRegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse("register")

    def test_register_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
