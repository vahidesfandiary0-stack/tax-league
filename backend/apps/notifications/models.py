from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        PAYMENT_APPROVED = "payment_approved", "تأیید پرداخت"
        PAYMENT_REJECTED = "payment_rejected", "رد پرداخت"
        SUBSCRIPTION_ACTIVATED = "subscription_activated", "فعال‌شدن اشتراک"
        EXAM_RESULT = "exam_result", "نتیجه آزمون"
        SUPPORT_REPLY = "support_reply", "پاسخ پشتیبانی"

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


class ShowcaseSlide(models.Model):
    class Kind(models.TextChoices):
        FOUNDER = "founder", "بنیان‌گذار"
        LOGO = "logo", "لوگوی لیگ"
        MESSAGE = "message", "پیام مدیریتی"
        ADVERTISEMENT = "advertisement", "تبلیغات"

    kind = models.CharField(max_length=20, choices=Kind.choices)
    title = models.CharField(max_length=160, blank=True)
    body = models.TextField(max_length=1200)
    image_url = models.URLField(max_length=1000, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    duration_seconds = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(3), MaxValueValidator(15)]
    )
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "اسلاید مدیریتی صفحه خانه"
        verbose_name_plural = "اسلایدهای مدیریتی صفحه خانه"

    def __str__(self):
        return self.title or self.get_kind_display()
