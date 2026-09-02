from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import JobApp

User = get_user_model()


class SearchJobTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        self.url = reverse("search")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"/users/login/?next={self.url}"
        )

    def test_get_renders_empty_search_page(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobapps/search_job.html")
        self.assertNotIn("jobapps", response.context)
        self.assertNotIn("count", response.context)
        self.assertNotIn("search_terms", response.context)

    def test_post_matches_by_company(self):
        match = JobApp.objects.create(
            user=self.user, company="Acme Corp", title="Engineer",
            description="Build things", job_status="Applied",
            location_type="Remote",
        )
        JobApp.objects.create(
            user=self.user, company="Globex", title="Engineer",
            description="Build other things", job_status="Applied",
            location_type="Remote",
        )

        response = self.client.post(self.url, {"search_terms": "acme"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["count"], 1)
        self.assertIn(match, response.context["jobapps"])
        self.assertEqual(response.context["search_terms"], "acme")

    def test_post_matches_by_description_case_insensitive(self):
        match = JobApp.objects.create(
            user=self.user, company="Acme", title="Engineer",
            description="Experience with PYTHON required",
            job_status="Applied", location_type="Remote",
        )

        response = self.client.post(self.url, {"search_terms": "python"})

        self.assertEqual(response.context["count"], 1)
        self.assertIn(match, response.context["jobapps"])

    def test_post_matches_by_job_id(self):
        match = JobApp.objects.create(
            user=self.user, company="Acme", title="Engineer",
            description="desc", job_id="REQ-12345",
            job_status="Applied", location_type="Remote",
        )

        response = self.client.post(self.url, {"search_terms": "REQ-123"})

        self.assertEqual(response.context["count"], 1)
        self.assertIn(match, response.context["jobapps"])

    def test_post_no_matches_returns_empty_results(self):
        JobApp.objects.create(
            user=self.user, company="Acme", title="Engineer",
            description="desc", job_status="Applied", location_type="Remote",
        )

        response = self.client.post(self.url, {"search_terms": "nonexistent-term-xyz"})

        self.assertEqual(response.context["count"], 0)
        self.assertEqual(list(response.context["jobapps"]), [])

    def test_post_orders_by_created_dt_descending(self):
        older = JobApp.objects.create(
            user=self.user, company="Acme", title="Older",
            description="matchterm", job_status="Applied", location_type="Remote",
        )
        newer = JobApp.objects.create(
            user=self.user, company="Acme", title="Newer",
            description="matchterm", job_status="Applied", location_type="Remote",
        )

        response = self.client.post(self.url, {"search_terms": "matchterm"})
        result_ids = [job.id for job in response.context["jobapps"]]

        self.assertEqual(result_ids, [newer.id, older.id])


    def test_post_excludes_other_users_jobapps(self):
        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        other_jobapp = JobApp.objects.create(
            user=other_user, company="Acme", title="Engineer",
            description="matchterm", job_status="Applied", location_type="Remote",
        )

        response = self.client.post(self.url, {"search_terms": "matchterm"})

        self.assertNotIn(other_jobapp, response.context["jobapps"])
        self.assertEqual(response.context["count"], 0)
