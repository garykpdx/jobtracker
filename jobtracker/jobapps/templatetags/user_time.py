from django import template
from django.utils import timezone as django_timezone

register = template.Library()


@register.filter
def user_localtime(value, user):
    """
    Convert a stored (UTC) datetime to the given user's chosen timezone.
    Falls back to Django's default TIME_ZONE if the user has no profile
    or hasn't set one yet.
    Usage: {{ jobapp.applied_dt|user_localtime:request.user|date:"M d, Y g:i A" }}
    """
    if not value:
        return value

    user_tz = getattr(getattr(user, "profile", None), "timezone", None)
    if not user_tz:
        return django_timezone.localtime(value)

    return django_timezone.localtime(value, timezone=user_tz)