from django.conf import settings
from django.db import models
from timezone_field import TimeZoneField


class UserProfile(models.Model):
    timezone = TimeZoneField(
        null=True,
        blank=True,
        default=None,
        choices_display="WITH_GMT_OFFSET",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    def __str__(self):
        return f"{self.timezone or 'unset'}"