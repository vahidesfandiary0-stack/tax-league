import uuid

from django.conf import settings
from django.db import models


class TutorConversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_conversations",
    )
    title = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["user", "-updated_at"], name="tutor_user_updated_idx")]

    def __str__(self):
        return self.title or f"گفتگوی مربی {self.pk}"


class TutorMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "کاربر"
        ASSISTANT = "assistant", "مربی هوشمند"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        TutorConversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=12, choices=Role.choices)
    content = models.TextField()
    citations = models.JSONField(default=list, blank=True)
    confidence = models.CharField(max_length=16, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["conversation", "created_at"], name="tutor_msg_created_idx")]

    def __str__(self):
        return f"{self.get_role_display()} · {self.created_at:%Y-%m-%d %H:%M}"
