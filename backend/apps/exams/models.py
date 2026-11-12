import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Exam(models.Model):
    class Kind(models.TextChoices):
        DAILY = "daily", "آزمون روزانه"
        WEEKLY = "weekly", "آزمون هفتگی"
        MOCK = "mock", "آزمون جامع"

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشرشده"
        ARCHIVED = "archived", "بایگانی"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=16, choices=Kind.choices)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    max_attempts = models.PositiveSmallIntegerField(default=1)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    counts_for_league = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.duration_minutes < 1 or self.max_attempts < 1:
            raise ValidationError("مدت آزمون و تعداد دفعات مجاز باید حداقل یک باشد.")
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "پایان آزمون باید بعد از شروع آن باشد."})

    def save(self, *args, **kwargs):
        if self.pk and Exam.objects.filter(pk=self.pk, status=self.Status.PUBLISHED).exists():
            raise ValidationError("آزمون منتشرشده قابل ویرایش نیست؛ برای تغییر، آزمون جدید بسازید.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="exam_questions")
    question = models.ForeignKey("questions.Question", on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()
    points_correct = models.SmallIntegerField(default=10)
    points_wrong = models.SmallIntegerField(default=-3)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["exam", "position"], name="uq_exam_question_position"),
            models.UniqueConstraint(fields=["exam", "question"], name="uq_exam_question"),
        ]

    def save(self, *args, **kwargs):
        if Exam.objects.filter(pk=self.exam_id, status=Exam.Status.PUBLISHED).exists():
            raise ValidationError("ترکیب سؤال‌های آزمون منتشرشده قابل تغییر نیست.")
        if self.question.status != self.question.Status.PUBLISHED:
            raise ValidationError("فقط سؤال منتشرشده را می‌توان به آزمون افزود.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if Exam.objects.filter(pk=self.exam_id, status=Exam.Status.PUBLISHED).exists():
            raise ValidationError("سؤال‌های آزمون منتشرشده قابل حذف نیستند.")
        return super().delete(*args, **kwargs)


class ExamAttempt(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "در حال برگزاری"
        SUBMITTED = "submitted", "تحویل‌شده"
        EXPIRED = "expired", "مهلت‌تمام‌شده"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="exam_attempts")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.IN_PROGRESS)
    started_at = models.DateTimeField()
    deadline_at = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    correct_count = models.PositiveSmallIntegerField(default=0)
    wrong_count = models.PositiveSmallIntegerField(default=0)
    blank_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]
        indexes = [models.Index(fields=["user", "exam", "status"])]

    def __str__(self):
        return f"{self.user_id} · {self.exam_id}"


class AttemptQuestion(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="questions")
    source_question_id = models.UUIDField()
    position = models.PositiveSmallIntegerField()
    prompt = models.TextField()
    explanation = models.TextField(blank=True)
    subject = models.CharField(max_length=32)
    points_correct = models.SmallIntegerField(default=10)
    points_wrong = models.SmallIntegerField(default=-3)

    class Meta:
        ordering = ["position"]
        constraints = [models.UniqueConstraint(fields=["attempt", "position"], name="uq_attempt_question_position")]


class AttemptOption(models.Model):
    attempt_question = models.ForeignKey(AttemptQuestion, on_delete=models.CASCADE, related_name="options")
    source_option_id = models.BigIntegerField()
    position = models.PositiveSmallIntegerField()
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["attempt_question", "position"], name="uq_attempt_option_position"),
        ]


class AttemptAnswer(models.Model):
    attempt_question = models.OneToOneField(AttemptQuestion, on_delete=models.CASCADE, related_name="answer")
    selected_option = models.ForeignKey(AttemptOption, on_delete=models.PROTECT, null=True, blank=True)
    answered_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.selected_option_id and self.selected_option.attempt_question_id != self.attempt_question_id:
            raise ValidationError("گزینه انتخاب‌شده متعلق به این سؤال نیست.")
