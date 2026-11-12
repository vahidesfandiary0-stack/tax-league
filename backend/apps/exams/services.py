from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    AttemptAnswer, AttemptOption, AttemptQuestion, Exam, ExamAttempt,
    ExamQuestion,
)


@transaction.atomic
def start_attempt(exam_id, user):
    exam = Exam.objects.select_for_update().get(pk=exam_id, status=Exam.Status.PUBLISHED)
    now = timezone.now()
    if exam.starts_at and now < exam.starts_at:
        raise ValidationError("زمان شروع آزمون فرا نرسیده است.")
    if exam.ends_at and now > exam.ends_at:
        raise ValidationError("مهلت شروع این آزمون به پایان رسیده است.")
    if exam.requires_purchase:
        from apps.payments.models import PurchasedExamAccess
        from apps.subscriptions.models import UserSubscription
        has_exam_access = PurchasedExamAccess.objects.filter(user=user, exam=exam).exists()
        has_active_subscription = UserSubscription.objects.filter(
            user=user, status=UserSubscription.Status.ACTIVE,
            starts_at__lte=now, ends_at__gt=now
        ).exists()
        if not (has_exam_access or has_active_subscription):
            raise ValidationError("برای شرکت در این آزمون باید خرید انجام دهید یا اشتراک فعال داشته باشید.")
    if not exam.exam_questions.exists():
        raise ValidationError("این آزمون هنوز سؤالی ندارد.")
    existing = ExamAttempt.objects.select_for_update().filter(
        exam=exam, user=user, status=ExamAttempt.Status.IN_PROGRESS
    ).first()
    if existing:
        return existing
    if ExamAttempt.objects.filter(exam=exam, user=user).count() >= exam.max_attempts:
        raise ValidationError("تعداد دفعات مجاز شرکت در آزمون تمام شده است.")
    attempt = ExamAttempt.objects.create(
        exam=exam, user=user, started_at=now,
        deadline_at=now + timedelta(minutes=exam.duration_minutes),
    )
    for item in exam.exam_questions.select_related("question").prefetch_related("question__options").all():
        snapshot = AttemptQuestion.objects.create(
            attempt=attempt, source_question_id=item.question_id,
            position=item.position, prompt=item.question.prompt,
            explanation=item.question.explanation, subject=item.question.subject,
            points_correct=item.points_correct, points_wrong=item.points_wrong,
        )
        for option in item.question.options.all():
            AttemptOption.objects.create(
                attempt_question=snapshot, source_option_id=option.pk,
                position=option.position, text=option.text, is_correct=option.is_correct,
            )
    return attempt


@transaction.atomic
def save_answer(attempt_id, question_id, option_id, user):
    attempt = ExamAttempt.objects.select_for_update().get(pk=attempt_id, user=user)
    if attempt.status != ExamAttempt.Status.IN_PROGRESS:
        raise ValidationError("این تلاش آزمون فعال نیست.")
    if timezone.now() >= attempt.deadline_at:
        raise ValidationError("زمان پاسخ‌گویی به پایان رسیده است.")
    question = AttemptQuestion.objects.get(pk=question_id, attempt=attempt)
    option = AttemptOption.objects.get(pk=option_id, attempt_question=question)
    answer, _ = AttemptAnswer.objects.update_or_create(
        attempt_question=question, defaults={"selected_option": option}
    )
    return answer


@transaction.atomic
def finalize_attempt(attempt_id, user):
    attempt = ExamAttempt.objects.select_for_update().get(pk=attempt_id, user=user)
    if attempt.status != ExamAttempt.Status.IN_PROGRESS:
        return attempt
    now = timezone.now()
    if now < attempt.deadline_at:
        # Early submission is allowed; the client cannot extend the server deadline.
        pass
    score = correct = wrong = blank = 0
    for question in attempt.questions.prefetch_related("options", "answer__selected_option"):
        answer = getattr(question, "answer", None)
        selected = answer.selected_option if answer else None
        if selected is None:
            blank += 1
        elif selected.is_correct:
            correct += 1
            score += question.points_correct
        else:
            wrong += 1
            score += question.points_wrong
    attempt.score = score
    attempt.correct_count = correct
    attempt.wrong_count = wrong
    attempt.blank_count = blank
    attempt.status = ExamAttempt.Status.SUBMITTED if now < attempt.deadline_at else ExamAttempt.Status.EXPIRED
    attempt.submitted_at = now
    attempt.save(update_fields=["score", "correct_count", "wrong_count", "blank_count", "status", "submitted_at"])
    if attempt.exam.counts_for_league:
        from apps.league.services import record_attempt_score
        record_attempt_score(attempt.pk)
    from apps.notifications.models import Notification
    from apps.notifications.services import create_notification
    create_notification(
        recipient=attempt.user,
        kind=Notification.Kind.EXAM_RESULT,
        title="نتیجه آزمون ثبت شد",
        body=f"آزمون «{attempt.exam.title}» به پایان رسید؛ امتیاز شما: {attempt.score}.",
        data={
            "attempt_id": attempt.pk, "exam_id": attempt.exam_id,
            "score": attempt.score, "correct_count": attempt.correct_count,
            "wrong_count": attempt.wrong_count, "blank_count": attempt.blank_count,
        },
    )
    return attempt



@transaction.atomic
def publish_exam(exam_id):
    exam = Exam.objects.select_for_update().get(pk=exam_id)
    if exam.status != Exam.Status.DRAFT:
        raise ValidationError("فقط آزمون پیش‌نویس قابل انتشار است.")
    items = list(exam.exam_questions.select_related("question").prefetch_related("question__options"))
    if not items:
        raise ValidationError("برای انتشار، آزمون باید حداقل یک سؤال داشته باشد.")
    for item in items:
        if item.question.status != item.question.Status.PUBLISHED:
            raise ValidationError("همه سؤال‌های آزمون باید منتشرشده باشند.")
        if item.question.options.count() != 4 or item.question.options.filter(is_correct=True).count() != 1:
            raise ValidationError("هر سؤال باید چهار گزینه و دقیقاً یک پاسخ صحیح داشته باشد.")
    exam.status = Exam.Status.PUBLISHED
    exam.save(update_fields=["status"])
    return exam
