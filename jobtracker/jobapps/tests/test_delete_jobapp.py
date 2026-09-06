from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from jobapps.models import JobApp

User = get_user_model()


class DeleteJobAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass123")

        self.jobapp = JobApp.objects.create(
            user=self.user,
            title="Software Engineer",
            company="Acme Corp",
            applied_dt=timezone.now(),
            city="Austin",
            state="TX",
            locality="Remote",
            job_id="12345",
            location_type="Remote",
            contractor_name="",
            job_status="Applied",
            payrate="100000",
            job_source="LinkedIn",
            job_url="",
            description="A great job.",
        )

        self.client.login(username="testuser", password="testpass123")

    def test_delete_removes_jobapp(self):
        """POSTing to the delete URL removes the JobApp and redirects to the list."""
        url = reverse("delete-job", kwargs={"job_id": self.jobapp.id})
        response = self.client.post(url)

        self.assertRedirects(response, reverse("jobapps"))
        self.assertFalse(JobApp.objects.filter(id=self.jobapp.id).exists())

    def test_delete_requires_login(self):
        """Anonymous users cannot delete a job app."""
        self.client.logout()
        url = reverse("delete-job", kwargs={"job_id": self.jobapp.id})
        response = self.client.post(url)

        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(JobApp.objects.filter(id=self.jobapp.id).exists())

    def test_delete_get_does_not_delete(self):
        """A GET request should not delete the job app (only POST should)."""
        url = reverse("delete-job", kwargs={"job_id": self.jobapp.id})
        response = self.client.get(url)

        self.assertRedirects(response, reverse("jobapp", kwargs={"job_id": self.jobapp.id}))
        self.assertTrue(JobApp.objects.filter(id=self.jobapp.id).exists())

    def test_cannot_delete_other_users_jobapp(self):
        """A user cannot delete another user's job app."""
        self.client.logout()
        self.client.login(username="otheruser", password="testpass123")

        url = reverse("delete-job", kwargs={"job_id": self.jobapp.id})
        response = self.client.post(url)

        self.assertRedirects(response, reverse("jobapps"))
        self.assertTrue(JobApp.objects.filter(id=self.jobapp.id).exists())