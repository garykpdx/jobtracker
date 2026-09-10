from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from jobapps.models import JobApp

User = get_user_model()


class EditJobappTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        self.jobapp = JobApp.objects.create(
            user=self.user,
            company="Acme Corp",
            title="Software Engineer",
            job_status="applied",
            description="<p>Original</p>",
            location_type="Remote",
            # add any other required fields for JobApp here
        )

        self.other_jobapp = JobApp.objects.create(
            user=self.other_user,
            company="Other Co",
            title="Other Title",
            job_status="applied",
            description="<p>Not yours</p>",
            location_type="Remote",
        )

    def _url(self, job_id):
        return reverse("edit-job", kwargs={"job_id": job_id})

    def test_requires_login(self):
        self.client.logout()
        url = self._url(self.jobapp.id)
        response = self.client.get(url)
        self.assertRedirects(response, f"/users/login/?next={url}")

    def test_get_renders_form_with_existing_data(self):
        response = self.client.get(self._url(self.jobapp.id))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobapps/edit_jobapp.html")
        self.assertEqual(response.context["jobapp"], self.jobapp)
        self.assertIn("form", response.context)
        self.assertIn("status_types", response.context)
        self.assertEqual(response.context["form"].instance, self.jobapp)

    def test_returns_redirect_when_not_found(self):
        response = self.client.get(self._url(9999))
        self.assertRedirects(response, reverse("jobapps"))

    def test_returns_redirect_when_not_owner(self):
        response = self.client.get(self._url(self.other_jobapp.id))
        self.assertRedirects(response, reverse("jobapps"))

    def test_post_valid_data_updates_and_redirects(self):
        data = {
            "company": "Acme Corp",
            "title": "Senior Software Engineer",
            "job_status": "Interviewed",  # <-- fixed casing/value
            "description": "<p>Updated</p><script>alert('xss')</script>",
            "location_type": "Remote",
        }
        response = self.client.post(self._url(self.jobapp.id), data)

        self.assertRedirects(
            response, reverse("jobapp", kwargs={"job_id": self.jobapp.id})
        )

        self.jobapp.refresh_from_db()
        self.assertEqual(self.jobapp.title, "Senior Software Engineer")
        self.assertEqual(self.jobapp.job_status, "Interviewed")  # <-- matches
        self.assertNotIn("<script>", self.jobapp.description)
        self.assertIn("<p>Updated</p>", self.jobapp.description)

    def test_post_invalid_data_rerenders_form_with_errors(self):
        data = {
            "company": "",  # required field left blank
            "title": "Senior Software Engineer",
            "job_status": "interviewing",
            "description": "<p>Updated</p>",
            "location_type": "Remote",
        }
        response = self.client.post(self._url(self.jobapp.id), data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobapps/edit_jobapp.html")
        self.assertTrue(response.context["form"].errors)
        self.assertIn("company", response.context["form"].errors)

        self.jobapp.refresh_from_db()
        self.assertEqual(self.jobapp.title, "Software Engineer")  # unchanged