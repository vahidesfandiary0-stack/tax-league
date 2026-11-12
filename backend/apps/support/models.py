import uuid

from django.conf import settings
from django.db import models


class SupportTicket(models.Model):
    class Category(models.TextChoices):
        ACCOUNT = "account", "حساب کاربری"
        PAYMENT = "payment", "پرداخت و اشتراک"
        EXAM = "exam", "آزمون"
        LEAGUE = "league", "لیگ و رتبه‌بندی"
        TECHNICAL = "technical", "مشکل فنی"
        OTHER = "other", "سایر"

    class Status(models.TextChoices):
        OPEN = "open", "باز"
        IN_PROGRESS = "in_progress", "در حال بررسی"
        WAITING_USER = "waiting_user", "منتظر پاسخ کاربر"
        ANSWERED = "answered", "پاسخ داده‌شده"
        CLOSED = "closed", "بسته‌شده"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="support_tickets")
    subject = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.id})"


class SupportMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="support_messages")
    body = models.TextField(max_length=4000)
    is_staff_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]

    def __str__(self):
        return f"پیام {self.pk} برای درخواست {self.ticket_id}"
