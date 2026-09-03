from datetime import datetime, time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import JobApp

User = get_user_model()


class JobAppListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        self.now = timezone.now()
        self.today = self.now.date()

    def _create_jobapp(self, user, job_status, applied_dt):
        """
        Create a JobApp and force applied_dt to the given timezone-aware
        datetime, bypassing auto_now_add.
        """
        jobapp = JobApp.objects.create(user=user, job_status=job_status)
        JobApp.objects.filter(id=jobapp.id).update(applied_dt=applied_dt)
        jobapp.refresh_from_db()
        return jobapp

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("jobapps"))
        self.assertRedirects(
            response, f"/users/login/?next={reverse('jobapps')}"
        )

    def test_list_renders_with_jobapps_in_range(self):
        jobapp = self._create_jobapp(
            self.user, "applied", self.now - timedelta(days=5)
        )

        response = self.client.get(reverse("jobapps"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "jobapps/jobapp_list.html")
        self.assertIn(jobapp, response.context["jobapps"])

    def test_excludes_jobapps_outside_date_range(self):
        old_jobapp = self._create_jobapp(
            self.user, "applied", self.now - timedelta(days=31)
        )

        response = self.client.get(reverse("jobapps"))

        self.assertNotIn(old_jobapp, response.context["jobapps"])

    def test_excludes_closed_jobapps(self):
        closed_jobapp = self._create_jobapp(
            self.user, "Closed", self.now - timedelta(days=5)
        )

        response = self.client.get(reverse("jobapps"))

        self.assertNotIn(closed_jobapp, response.context["jobapps"])

    def test_excludes_closed_jobapps_case_insensitive(self):
        closed_jobapp = self._create_jobapp(
            self.user, "closed", self.now - timedelta(days=5)
        )

        response = self.client.get(reverse("jobapps"))

        self.assertNotIn(closed_jobapp, response.context["jobapps"])

    def test_excludes_other_users_jobapps(self):
        other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        other_jobapp = self._create_jobapp(
            other_user, "applied", self.now - timedelta(days=5)
        )

        response = self.client.get(reverse("jobapps"))

        self.assertNotIn(other_jobapp, response.context["jobapps"])

    def test_includes_jobapp_applied_exactly_today(self):
        start_of_today = timezone.make_aware(datetime.combine(self.today, time.min))
        jobapp = self._create_jobapp(self.user, "applied", start_of_today)

        response = self.client.get(reverse("jobapps"))

        self.assertIn(jobapp, response.context["jobapps"])

    def test_includes_jobapp_applied_exactly_30_days_ago(self):
        thirty_days_ago = self.today - timedelta(days=30)
        end_of_that_day = timezone.make_aware(datetime.combine(thirty_days_ago, time.max))
        jobapp = self._create_jobapp(self.user, "applied", end_of_that_day)

        response = self.client.get(reverse("jobapps"))

        self.assertIn(jobapp, response.context["jobapps"])

    def test_orders_by_created_dt_descending(self):
        older = self._create_jobapp(
            self.user, "applied", self.now - timedelta(days=5)
        )
        newer = self._create_jobapp(
            self.user, "applied", self.now - timedelta(days=2)
        )

        response = self.client.get(reverse("jobapps"))
        result_ids = [job.id for job in response.context["jobapps"]]

        self.assertEqual(result_ids, [newer.id, older.id])
