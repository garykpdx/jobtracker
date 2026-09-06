from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

REQUIRED_FIELDS = ["company", "title", "job_status", "description", "location_type"]
OPTIONAL_FIELDS = ["job_id", "city", "state", "locality", "payrate",
                    "contractor_name", "job_url", "job_source"]


class RequiredFieldAsteriskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.login(username="testuser", password="testpass123")

    def _get_field_block(self, html, field_name):
        blocks = html.split("</p>")
        marker = f'id_{field_name}"'
        for block in blocks:
            if marker in block:
                return block + "</p>"
        self.fail(f"Could not find rendered block for field '{field_name}'")

    def test_required_fields_marked_with_required_css_class(self):
        response = self.client.get(reverse("new-job"))
        html = response.content.decode()

        for field_name in REQUIRED_FIELDS:
            block = self._get_field_block(html, field_name)
            self.assertIn(
                'class="required"', block,
                f"Field '{field_name}' should be marked required but is missing "
                f"the 'required' css class (asterisk would not display)"
            )

    def test_optional_fields_not_marked_required(self):
        response = self.client.get(reverse("new-job"))
        html = response.content.decode()

        for field_name in OPTIONAL_FIELDS:
            block = self._get_field_block(html, field_name)
            self.assertNotIn(
                'class="required"', block,
                f"Field '{field_name}' is optional but is incorrectly marked required"
            )

    def test_required_asterisk_css_rule_present(self):
        response = self.client.get(reverse("new-job"))
        html = response.content.decode()
        self.assertIn(".required label:after", html)