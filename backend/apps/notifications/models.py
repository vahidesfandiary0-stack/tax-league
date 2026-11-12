from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        PAYMENT_APPROVED = "payment_approved", "تأیید پرداخت"
        PAYMENT_REJECTED = "payment_rejected", "رد پرداخت"
        SUBSCRIPTION_ACTIVATED = "subscription_activated", "فعال‌شدن اشتراک"
        EXAM_RESULT = "exam_result", "نتیجه آزمون"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=40, choices=Kind.choices)
    title = models.CharField(max_length=160)
    body = models.CharField(max_length=500)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        indexes = [models.Index(fields=["recipient", "read_at", "-created_at"], name="notif_recipient_read_idx")]

    def __str__(self):
        return f"{self.recipient_id}: {self.title}"
