from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


class UserProfileTimezoneTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_new_userprofile_has_null_timezone(self):
        profile = UserProfile.objects.create(user=self.user)

        self.assertIsNone(profile.timezone)

    def test_get_or_create_gives_new_profile_null_timezone(self):
        # Mirrors how views actually create a profile on first visit
        profile, created = UserProfile.objects.get_or_create(user=self.user)

        self.assertTrue(created)
        self.assertIsNone(profile.timezone)

    def test_set_detected_timezone_sets_it_when_null(self):
        UserProfile.objects.create(user=self.user)

        response = self.client.post(
            reverse("users:set-timezone"),
            {"timezone": "America/New_York"},
        )

        self.assertEqual(response.status_code, 200)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(str(profile.timezone), "America/New_York")

    def test_set_detected_timezone_does_not_overwrite_existing_value(self):
        UserProfile.objects.create(user=self.user, timezone="Europe/Berlin")

        response = self.client.post(
            reverse("users:set-timezone"),
            {"timezone": "Asia/Tokyo"},
        )

        self.assertEqual(response.status_code, 200)

        profile = UserProfile.objects.get(user=self.user)
        # Still the original value — not overwritten by the second detection
        self.assertEqual(str(profile.timezone), "Europe/Berlin")

    def test_set_detected_timezone_rejects_invalid_timezone(self):
        UserProfile.objects.create(user=self.user)

        response = self.client.post(
            reverse("users:set-timezone"),
            {"timezone": "Not/ARealZone"},
        )

        self.assertEqual(response.status_code, 400)

        profile = UserProfile.objects.get(user=self.user)
        self.assertIsNone(profile.timezone)

    def test_set_detected_timezone_rejects_missing_timezone(self):
        UserProfile.objects.create(user=self.user)

        response = self.client.post(reverse("users:set-timezone"), {})

        self.assertEqual(response.status_code, 400)

    def test_set_detected_timezone_requires_login(self):
        self.client.logout()

        response = self.client.post(
            reverse("users:set-timezone"),
            {"timezone": "America/New_York"},
        )

        self.assertNotEqual(response.status_code, 200)

    def test_set_detected_timezone_requires_post(self):
        UserProfile.objects.create(user=self.user)

        response = self.client.get(reverse("users:set-timezone"))

        self.assertEqual(response.status_code, 405)
