import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class RegulationSource(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="نام منبع")
    base_url = models.URLField(max_length=1000, verbose_name="نشانی منبع")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    check_interval_hours = models.PositiveIntegerField(default=24)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "منبع مقررات"
        verbose_name_plural = "منابع مقررات"

    def __str__(self):
        return self.name


class RegulationDocument(models.Model):
    class DocumentType(models.TextChoices):
        LAW = "law", "قانون"
        BYLAW = "bylaw", "آیین‌نامه"
        CIRCULAR = "circular", "بخشنامه"
        INSTRUCTION = "instruction", "دستورالعمل"
        RULING = "ruling", "رأی"
        OTHER = "other", "سایر"

    class LegalStatus(models.TextChoices):
        VALID = "valid", "معتبر"
        AMENDED = "amended", "اصلاح‌شده"
        REPEALED = "repealed", "منسوخ"
        ANNULLED = "annulled", "ابطال‌شده"
        EXPIRED = "expired", "منقضی"
        UNKNOWN = "unknown", "نامشخص"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        RegulationSource,
        on_delete=models.PROTECT,
        related_name="documents",
    )
    external_id = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=1000, verbose_name="عنوان")
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
    )
    official_number = models.CharField(max_length=200, blank=True)
    issuing_authority = models.CharField(max_length=300, blank=True)
    original_url = models.URLField(max_length=1500)
    approval_date = models.DateField(null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_until = models.DateField(null=True, blank=True)
    legal_status = models.CharField(
        max_length=20,
        choices=LegalStatus.choices,
        default=LegalStatus.UNKNOWN,
    )
    invalidity_reason = models.TextField(blank=True)
    latest_version = models.PositiveIntegerField(default=0)
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publication_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"],
                condition=~models.Q(external_id=""),
                name="uq_reg_source_external_id",
            ),
        ]
        indexes = [
            models.Index(fields=["document_type", "legal_status"]),
            models.Index(fields=["official_number"]),
            models.Index(fields=["effective_from", "effective_until"]),
        ]
        verbose_name = "سند مقرراتی"
        verbose_name_plural = "اسناد مقرراتی"

    def clean(self):
        super().clean()
        if self.effective_from and self.effective_until:
            if self.effective_until < self.effective_from:
                raise ValidationError({
                    "effective_until": "پایان اعتبار نمی‌تواند قبل از شروع اعتبار باشد."
                })

    def __str__(self):
        return self.title


class RegulationVersion(models.Model):
    document = models.ForeignKey(
        RegulationDocument,
        on_delete=models.PROTECT,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField()
    content = models.TextField(blank=True)
    content_sha256 = models.CharField(max_length=64)
    original_file = models.FileField(
        upload_to="private-regulations/%Y/%m/",
        blank=True,
    )
    extraction_method = models.CharField(max_length=30, blank=True)
    extraction_quality = models.PositiveSmallIntegerField(null=True, blank=True)
    source_metadata = models.JSONField(default=dict, blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reviewed_regulation_versions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["document", "version_number"],
                name="uq_reg_document_version",
            ),
            models.UniqueConstraint(
                fields=["document", "content_sha256"],
                name="uq_reg_document_content_hash",
            ),
        ]
        verbose_name = "نسخه مقرره"
        verbose_name_plural = "نسخه‌های مقررات"

    def save(self, *args, **kwargs):
        if self.pk and RegulationVersion.objects.filter(pk=self.pk).exists():
            raise ValidationError("نسخه ثبت‌شده مقرره غیرقابل ویرایش است.")
        if self.document_id and self.version_number <= 0:
            raise ValidationError("شماره نسخه باید مثبت باشد.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("نسخه‌های مقررات قابل حذف نیستند.")

    def __str__(self):
        return f"{self.document.title} · نسخه {self.version_number}"


class RegulationChange(models.Model):
    class ChangeType(models.TextChoices):
        NEW = "new", "سند جدید"
        CONTENT = "content", "تغییر متن"
        STATUS = "status", "تغییر وضعیت اعتبار"
        DATE = "date", "تغییر تاریخ اعتبار"
        METADATA = "metadata", "تغییر مشخصات"
        POSSIBLE = "possible", "تغییر احتمالی"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        CONFIRMED = "confirmed", "تأییدشده"
        REJECTED = "rejected", "ردشده"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        RegulationDocument,
        on_delete=models.PROTECT,
        related_name="changes",
    )
    old_version = models.ForeignKey(
        RegulationVersion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="changes_from",
    )
    new_version = models.ForeignKey(
        RegulationVersion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="changes_to",
    )
    change_type = models.CharField(max_length=20, choices=ChangeType.choices)
    summary = models.TextField(blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reviewed_regulation_changes",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["review_status", "detected_at"]),
            models.Index(fields=["change_type", "detected_at"]),
        ]
        verbose_name = "تغییر مقررات"
        verbose_name_plural = "تغییرات مقررات"

    def __str__(self):
        return f"{self.document.title} · {self.get_change_type_display()}"
