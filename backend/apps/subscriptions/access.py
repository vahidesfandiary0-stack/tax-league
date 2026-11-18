from django.utils import timezone

from .models import UserSubscription


def has_active_academy_access(user, *, at=None):
    """Single server-side entitlement check for all subscriber-only features."""
    if not user or not user.is_authenticated:
        return False
    now = at or timezone.now()
    return UserSubscription.objects.filter(
        user=user,
        status=UserSubscription.Status.ACTIVE,
        starts_at__lte=now,
        ends_at__gt=now,
    ).exists()
