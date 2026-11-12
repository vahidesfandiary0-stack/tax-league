import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Question(models.Model):
    class Subject(models.TextChoices):
        DIRECT_TAX = "direct_tax", "مالیات‌های مستقیم"
        VAT = "vat", "مالیات بر ارزش افزوده"
        TAXPAYER_SYSTEM = "taxpayer_system", "سامانه مؤدیان و پایانه‌های فروشگاهی"
        DISPUTES = "disputes", "دادرسی مالیاتی"
        AUDIT = "audit", "حسابرسی مالیاتی"
        OTHER_LAWS = "other_laws", "قوانین و مقررات مرتبط"

    class Difficulty(models.TextChoices):
        EASY = "easy", "آسان"
        MEDIUM = "medium", "متوسط"
        HARD = "hard", "سخت"

    class Provenance(models.TextChoices):
        OFFICIAL = "official", "متن رسمی آزمون"
        RECONSTRUCTED = "reconstructed", "بازسازی‌شده از منبع"
        AUTHORED = "authored", "تألیفی"

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PENDING = "pending_review", "در انتظار بررسی"
        APPROVED = "approved", "تأییدشده"
        REJECTED = "rejected", "ردشده"
        PUBLISHED = "published", "منتشرشده"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=32, choices=Subject.choices)
    difficulty = models.CharField(max_length=12, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    prompt = models.TextField()
    explanation = models.TextField(blank=True)
    source_reference = models.CharField(max_length=500, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    provenance = models.CharField(max_length=20, choices=Provenance.choices, default=Provenance.AUTHORED)
    provenance_note = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    version = models.PositiveIntegerField(default=1)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="authored_questions")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="reviewed_questions")
    review_decision = models.CharField(max_length=20, blank=True)
    review_reason = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["id", "version"], name="uq_question_id_version"),
        ]
        indexes = [models.Index(fields=["status", "subject"], name="questions_status_subject_idx"), models.Index(fields=["provenance"], name="questions_provenance_idx")]

    def save(self, *args, **kwargs):
        if self.pk and Question.objects.filter(pk=self.pk, status=self.Status.PUBLISHED).exists():
            raise ValidationError("سؤال منتشرشده قابل ویرایش نیست؛ برای اصلاح باید نسخه جدید ساخته شود.")
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValidationError({"valid_until": "تاریخ پایان اعتبار نمی‌تواند قبل از تاریخ شروع باشد."})
        if self.reviewer_id and self.reviewer_id == self.author_id:
            raise ValidationError({"reviewer": "نویسنده مجاز به بررسی سؤال خودش نیست."})

    def __str__(self):
        return f"{self.get_subject_display()} · {self.id}"


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    position = models.PositiveSmallIntegerField()
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["question", "position"], name="uq_question_option_position"),
            models.CheckConstraint(condition=models.Q(position__gte=1, position__lte=4), name="ck_question_option_position_1_4"),
        ]

    def save(self, *args, **kwargs):
        if self.pk and Question.objects.filter(pk=self.question_id, status=Question.Status.PUBLISHED).exists():
            raise ValidationError("گزینه سؤال منتشرشده قابل ویرایش نیست.")
        if Question.objects.filter(pk=self.question_id, status=Question.Status.PUBLISHED).exists():
            raise ValidationError("برای سؤال منتشرشده نمی‌توان گزینه جدید افزود.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if Question.objects.filter(pk=self.question_id, status=Question.Status.PUBLISHED).exists():
            raise ValidationError("گزینه سؤال منتشرشده قابل حذف نیست.")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.question_id} / گزینه {self.position}"
