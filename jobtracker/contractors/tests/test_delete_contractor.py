from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from contractors.models import Contractor

User = get_user_model()


class DeleteContractorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass123")

        self.contractor = Contractor.objects.create(
            app_user=self.user,
            name="Jane Smith",
            company="Staffing Co",
            phone="555-1234",
            email="jane@staffingco.com",
        )

        self.client.login(username="testuser", password="testpass123")

    def test_delete_removes_contractor(self):
        url = reverse("contractors:delete_contractor", kwargs={"contractor_id": self.contractor.id})
        response = self.client.post(url)

        self.assertRedirects(response, reverse("contractors:contractor_list"))
        self.assertFalse(Contractor.objects.filter(id=self.contractor.id).exists())

    def test_delete_requires_login(self):
        self.client.logout()
        url = reverse("contractors:delete_contractor", kwargs={"contractor_id": self.contractor.id})
        response = self.client.post(url)

        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(Contractor.objects.filter(id=self.contractor.id).exists())

    def test_delete_get_does_not_delete(self):
        url = reverse("contractors:delete_contractor", kwargs={"contractor_id": self.contractor.id})
        response = self.client.get(url)

        self.assertRedirects(
            response,
            reverse("contractors:contractor_page", kwargs={"contractor_id": self.contractor.id}),
        )
        self.assertTrue(Contractor.objects.filter(id=self.contractor.id).exists())

    def test_cannot_delete_other_users_contractor(self):
        self.client.logout()
        self.client.login(username="otheruser", password="testpass123")

        url = reverse("contractors:delete_contractor", kwargs={"contractor_id": self.contractor.id})
        response = self.client.post(url)

        self.assertRedirects(response, reverse("contractors:contractor_list"))
        self.assertTrue(Contractor.objects.filter(id=self.contractor.id).exists())

    def test_delete_nonexistent_contractor_redirects(self):
        url = reverse("contractors:delete_contractor", kwargs={"contractor_id": 99999})
        response = self.client.post(url)

        self.assertRedirects(response, reverse("contractors:contractor_list"))