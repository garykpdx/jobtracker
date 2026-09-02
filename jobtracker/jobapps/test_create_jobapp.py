from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import JobApp

User = get_user_model()


class NewJobAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        self.url = reverse("new-job")

        self.valid_data = {
            "company": "Acme Corp",
            "title": "Software Engineer",
            "job_status": "Applied",
            "description": "<p>Great role</p><script>alert('xss')</script>",
            "location_type": "Remote",
            # optional fields omitted: job_id, city, state, locality,
            # payrate, contractor_name, job_url, job_source
        }

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"/users/login/?next={self.url}"
        )

    def test_get_renders_empty_form(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobapps/new_jobapp.html")
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_bound)

    def test_post_valid_data_creates_jobapp_and_redirects(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, reverse("jobapps"))
        self.assertEqual(JobApp.objects.count(), 1)

        jobapp = JobApp.objects.first()
        self.assertEqual(jobapp.user, self.user)
        self.assertEqual(jobapp.company, "Acme Corp")
        self.assertEqual(jobapp.title, "Software Engineer")
        self.assertEqual(jobapp.job_status, "Applied")
        self.assertEqual(jobapp.location_type, "Remote")

    def test_post_sanitizes_description_with_bleach(self):
        self.client.post(self.url, self.valid_data)

        jobapp = JobApp.objects.first()
        self.assertNotIn("<script>", jobapp.description)
        self.assertNotIn("alert(", jobapp.description)
        # allowed tag should survive
        self.assertIn("<p>", jobapp.description)

    def test_post_missing_required_field_does_not_create_jobapp(self):
        invalid_data = self.valid_data.copy()
        invalid_data["company"] = ""

        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobapps/new_jobapp.html")
        self.assertTrue(response.context["form"].errors)
        self.assertIn("company", response.context["form"].errors)
        self.assertEqual(JobApp.objects.count(), 0)

    def test_post_invalid_choice_does_not_create_jobapp(self):
        invalid_data = self.valid_data.copy()
        invalid_data["job_status"] = "NotARealStatus"

        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertIn("job_status", response.context["form"].errors)
        self.assertEqual(JobApp.objects.count(), 0)