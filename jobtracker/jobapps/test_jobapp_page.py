from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import JobApp, JobComment

User = get_user_model()


class JobAppPageHappyPathTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        self.jobapp = JobApp.objects.create(
            user=self.user,
            job_status="applied",
            # add other required fields for JobApp here
        )

    def test_get_jobapp_page_renders_successfully(self):
        url = reverse("jobapp", kwargs={"job_id": self.jobapp.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobapps/jobapp_page.html")
        self.assertEqual(response.context["jobapp"], self.jobapp)
        self.assertIn("status_types", response.context)
        self.assertIn("job_comments", response.context)

    def test_post_updates_status_adds_comment_and_deletes_comment(self):
        # Existing comment to be deleted
        existing_comment = JobComment.objects.create(
            user=self.user,
            jobapp=self.jobapp,
            text="old comment",
            change_dt=timezone.now(),
        )

        url = reverse("jobapp", kwargs={"job_id": self.jobapp.id})
        response = self.client.post(url, {
            "job_status_update": "interviewing",
            "comment_text": "Had a great first call",
            "delete_comment_id": existing_comment.id,
        })

        # Should redirect back to the same jobapp page
        self.assertRedirects(
            response, reverse("jobapp", kwargs={"job_id": self.jobapp.id})
        )

        self.jobapp.refresh_from_db()
        self.assertEqual(self.jobapp.job_status, "interviewing")

        self.assertFalse(
            JobComment.objects.filter(id=existing_comment.id).exists()
        )
        self.assertTrue(
            JobComment.objects.filter(
                jobapp=self.jobapp, text="Had a great first call"
            ).exists()
        )