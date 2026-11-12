import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class SubscriptionPlan(models.Model):
    class Period(models.TextChoices):
        MONTHLY = "monthly", "ماهانه"
        QUARTERLY = "quarterly", "سه‌ماهه"
        ANNUAL = "annual", "سالانه"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    period = models.CharField(max_length=12, choices=Period.choices, unique=True)
    duration_days = models.PositiveSmallIntegerField()
    price_irr = models.PositiveBigIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["duration_days"]

    def clean(self):
        if self.duration_days < 1 or self.price_irr < 1:
            raise ValidationError("مدت و مبلغ طرح باید بیشتر از صفر باشد.")

    def __str__(self):
        return f"{self.title} · {self.price_irr:,} ریال"


class UserSubscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "فعال"
        EXPIRED = "expired", "منقضی"
        REVOKED = "revoked", "لغوشده"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    source_order = models.OneToOneField("payments.PaymentOrder", on_delete=models.PROTECT, related_name="granted_subscription")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ends_at"]
        indexes = [models.Index(fields=["user", "status", "ends_at"], name="subs_user_status_end_idx")]

    def clean(self):
        if self.ends_at <= self.starts_at:
            raise ValidationError("پایان اشتراک باید بعد از شروع آن باشد.")

    def __str__(self):
        return f"{self.user} · {self.plan}"
