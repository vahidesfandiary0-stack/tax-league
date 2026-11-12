import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class LeagueSeason(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        ACTIVE = "active", "فعال"
        CLOSED = "closed", "پایان‌یافته"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=160)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-starts_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(ends_at__gt=models.F("starts_at")), name="league_season_dates_valid"),
        ]

    def clean(self):
        if self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "پایان فصل باید بعد از شروع آن باشد."})

    def save(self, *args, **kwargs):
        if self.pk and LeagueSeason.objects.filter(pk=self.pk).exclude(status=self.Status.DRAFT).exists():
            old = LeagueSeason.objects.get(pk=self.pk)
            if old.status != self.status or old.title != self.title or old.starts_at != self.starts_at or old.ends_at != self.ends_at:
                raise ValidationError("فصل فعال یا پایان‌یافته قابل ویرایش نیست.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class LeagueScoreEntry(models.Model):
    """Immutable, one-per-attempt ledger entry for an official league exam."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.ForeignKey(LeagueSeason, on_delete=models.PROTECT, related_name="score_entries")
    attempt = models.OneToOneField("exams.ExamAttempt", on_delete=models.PROTECT, related_name="league_entry")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="league_score_entries")
    score = models.IntegerField()
    correct_count = models.PositiveSmallIntegerField()
    wrong_count = models.PositiveSmallIntegerField()
    elapsed_seconds = models.PositiveIntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score", "-correct_count", "wrong_count", "elapsed_seconds"]
        indexes = [
            models.Index(fields=["season", "user"]),
            models.Index(fields=["season", "-score"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk and LeagueScoreEntry.objects.filter(pk=self.pk).exists():
            raise ValidationError("رکورد امتیاز لیگ غیرقابل‌ویرایش است.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("رکورد امتیاز لیگ قابل حذف نیست.")
