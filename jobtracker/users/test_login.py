from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginNextRedirectTests(TestCase):
    def setUp(self):
        User.objects.create_user("tester", password="pw-12345-xyz")
        self.url = reverse("users:login")

    def post_login(self, next_value):
        data = {"username": "tester", "password": "pw-12345-xyz"}
        if next_value is not None:
            data["next"] = next_value
        return self.client.post(self.url, data)

    def test_safe_next_is_followed(self):
        resp = self.post_login("/users/profile/")
        self.assertRedirects(resp, "/users/profile/", fetch_redirect_response=False)

    def test_unsafe_next_values_fall_back(self):
        for bad in ["https://evil.com", "//evil.com", "javascript:alert(1)", ""]:
            with self.subTest(next=bad):
                self.client.logout()
                resp = self.post_login(bad)
                self.assertRedirects(resp, reverse("jobapps"), fetch_redirect_response=False)