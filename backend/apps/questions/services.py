from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Question


@transaction.atomic
def submit_for_review(question_id, actor):
    question = Question.objects.select_for_update().get(pk=question_id)
    if question.author_id != actor.pk:
        raise ValidationError("فقط نویسنده می‌تواند سؤال خود را برای بررسی ارسال کند.")
    if question.status not in (Question.Status.DRAFT, Question.Status.REJECTED):
        raise ValidationError("وضعیت فعلی اجازه ارسال برای بررسی را نمی‌دهد.")
    if question.options.count() != 4:
        raise ValidationError("سؤال باید دقیقاً چهار گزینه داشته باشد.")
    if question.options.filter(is_correct=True).count() != 1:
        raise ValidationError("دقیقاً یک گزینه باید پاسخ صحیح باشد.")
    question.status = Question.Status.PENDING
    question.reviewer = None
    question.review_decision = ""
    question.review_reason = ""
    question.reviewed_at = None
    question.save(update_fields=["status", "reviewer", "review_decision", "review_reason", "reviewed_at", "updated_at"])
    return question


@transaction.atomic
def review_question(question_id, reviewer, approve, reason=""):
    question = Question.objects.select_for_update().get(pk=question_id)
    if question.status != Question.Status.PENDING:
        raise ValidationError("فقط سؤالِ در انتظار بررسی قابل تصمیم‌گیری است.")
    if question.author_id == reviewer.pk:
        raise ValidationError("نویسنده نمی‌تواند سؤال خودش را بررسی کند.")
    if approve and (question.options.count() != 4 or question.options.filter(is_correct=True).count() != 1):
        raise ValidationError("ساختار سؤال کامل نیست؛ چهار گزینه و یک پاسخ صحیح لازم است.")
    question.reviewer = reviewer
    question.review_decision = "approved" if approve else "rejected"
    question.review_reason = reason
    question.reviewed_at = timezone.now()
    question.status = Question.Status.APPROVED if approve else Question.Status.REJECTED
    question.save(update_fields=["reviewer", "review_decision", "review_reason", "reviewed_at", "status", "updated_at"])
    return question


@transaction.atomic
def publish_question(question_id, owner):
    """Owner-only final publication; independent review is optional, not mandatory."""
    if not getattr(owner, "is_superuser", False):
        raise ValidationError("انتشار نهایی فقط با تأیید مالک سامانه مجاز است.")
    question = Question.objects.select_for_update().get(pk=question_id)
    publishable_statuses = (
        Question.Status.DRAFT,
        Question.Status.PENDING,
        Question.Status.APPROVED,
    )
    if question.status not in publishable_statuses:
        raise ValidationError("فقط سؤال پیش‌نویس، در انتظار بررسی یا تأییدشده قابل انتشار است.")
    options = list(question.options.all())
    if len(options) != 4:
        raise ValidationError("سؤال باید دقیقاً چهار گزینه داشته باشد.")
    if sum(1 for option in options if option.is_correct) != 1:
        raise ValidationError("دقیقاً یک گزینه باید پاسخ صحیح باشد.")
    if not question.prompt.strip():
        raise ValidationError("متن سؤال نمی‌تواند خالی باشد.")
    if not question.explanation.strip():
        raise ValidationError("پاسخ تشریحی برای انتشار الزامی است.")
    if not question.source_reference.strip():
        raise ValidationError("منبع معتبر برای انتشار الزامی است.")
    if question.difficulty not in (
        Question.Difficulty.HARD,
        Question.Difficulty.VERY_HARD,
        Question.Difficulty.SPECIALIST,
    ):
        raise ValidationError("فقط سؤال سخت، خیلی سخت یا تخصصی قابل انتشار است.")

    now = timezone.now()
    question.status = Question.Status.PUBLISHED
    question.published_at = now
    # Record that the owner made the final decision without fabricating a reviewer.
    question.review_decision = "owner_published"
    question.review_reason = "انتشار مستقیم توسط مالک سامانه"
    question.reviewed_at = now
    question.save(update_fields=[
        "status", "published_at", "review_decision", "review_reason",
        "reviewed_at", "updated_at",
    ])
    return question
