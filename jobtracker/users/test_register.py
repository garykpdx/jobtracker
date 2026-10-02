from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()


class AdminRegisterUserTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="adminuser", password="adminpass123", email="admin@example.com"
        )
        self.regular_user = User.objects.create_user(
            username="regularuser", password="regularpass123"
        )
        self.url = reverse("users:register")
        self.valid_data = {
            "username": "newhire",
            "first_name": "New",
            "last_name": "Hire",
            "email": "newhire@example.com",
            "password1": "S0meStrongPass!23",
            "password2": "S0meStrongPass!23",
        }

    # --- Positive case ---

    def test_superuser_can_register_new_user(self):
        self.client.login(username="adminuser", password="adminpass123")

        response = self.client.post(self.url, self.valid_data)

        new_user = User.objects.filter(username="newhire").first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.email, "newhire@example.com")
        self.assertEqual(new_user.first_name, "New")

        # The admin's own session must be untouched — this is the bug where
        # the browser got logged into the newly created account instead.
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.admin.pk)

        # Admin should see a success message confirming it worked
        message_texts = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("newhire" in m for m in message_texts))

        self.assertRedirects(response, self.url)

    # --- Negative cases ---

    def test_non_superuser_cannot_register_new_user(self):
        self.client.login(username="regularuser", password="regularpass123")

        response = self.client.post(self.url, self.valid_data)

        # The core security check: no account should be created at all
        self.assertFalse(User.objects.filter(username="newhire").exists())
        self.assertRedirects(response, reverse("jobapps"))

        message_texts = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("permission" in m.lower() for m in message_texts))

    def test_anonymous_user_cannot_register_new_user(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertFalse(User.objects.filter(username="newhire").exists())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_non_superuser_get_request_also_blocked(self):
        """
        Confirms the fix covers GET too, not just POST — both must be
        checked the same way now.
        """
        self.client.login(username="regularuser", password="regularpass123")

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("jobapps"))

    def test_invalid_form_creates_no_user_and_shows_error(self):
        self.client.login(username="adminuser", password="adminpass123")
        invalid_data = self.valid_data.copy()
        invalid_data["password2"] = "doesnotmatch"

        response = self.client.post(self.url, invalid_data)

        self.assertFalse(User.objects.filter(username="newhire").exists())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

        message_texts = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("failed" in m.lower() for m in message_texts))
