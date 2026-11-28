from datetime import timedelta
import random

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    AttemptAnswer, AttemptOption, AttemptQuestion, Exam, ExamAttempt,
    ExamQuestion,
)


def _render_variant_text(template, values):
    if not values:
        return template
    try:
        return template.format_map(values)
    except (KeyError, ValueError, IndexError) as exc:
        raise ValidationError("قالب سؤال یا گزینه با متغیرهای تعریف‌شده سازگار نیست.") from exc


def _build_attempt_question(attempt, item, rng, position):
    question = item.question
    config = question.variant_config or {}
    variables_config = config.get("variables", {})
    if not isinstance(variables_config, dict):
        raise ValidationError("تعریف متغیرهای سؤال نامعتبر است.")
    values = {}
    for name, spec in variables_config.items():
        if not isinstance(name, str) or not name.isidentifier() or not isinstance(spec, dict):
            raise ValidationError("تعریف متغیر عددی سؤال نامعتبر است.")
        minimum, maximum = spec.get("min"), spec.get("max")
        step = spec.get("step", 1)
        if (not isinstance(minimum, int) or isinstance(minimum, bool)
                or not isinstance(maximum, int) or isinstance(maximum, bool)
                or not isinstance(step, int) or isinstance(step, bool)
                or step < 1 or maximum < minimum or (maximum - minimum) // step > 100000):
            raise ValidationError("بازه یا گام متغیر عددی سؤال نامعتبر است.")
        values[name] = minimum + rng.randrange((maximum - minimum) // step + 1) * step

    snapshot = AttemptQuestion.objects.create(
        attempt=attempt, source_question_id=question.pk, position=position,
        prompt=_render_variant_text(question.prompt, values),
        explanation=_render_variant_text(question.explanation, values),
        subject=question.subject, points_correct=item.points_correct,
        points_wrong=item.points_wrong,
    )
    options = list(question.options.all())
    rng.shuffle(options)
    for position, option in enumerate(options, start=1):
        AttemptOption.objects.create(
            attempt_question=snapshot, source_option_id=option.pk,
            position=position, text=_render_variant_text(option.text, values),
            is_correct=option.is_correct,
        )
    return snapshot


def start_attempt(exam_id, user):
    attempt, shared_window_closed = _start_attempt(exam_id, user)
    if shared_window_closed:
        raise ValidationError("مهلت آزمون شبانه به پایان رسیده است.")
    return attempt


@transaction.atomic
def _start_attempt(exam_id, user):
    # Serialize starts only for the same participant. Locking the shared Exam row
    # here would queue every participant behind one database row at the league start.
    user = user.__class__.objects.select_for_update().get(pk=user.pk)
    exam = Exam.objects.get(pk=exam_id, status=Exam.Status.PUBLISHED)
    now = timezone.now()
    is_night = exam.kind == Exam.Kind.NIGHT
    if is_night:
        if not exam.counts_for_league or exam.requires_purchase:
            raise ValidationError("آزمون شبانه رسمی باید رایگان و مؤثر در لیگ باشد.")
        if not exam.starts_at or not exam.ends_at or exam.ends_at <= exam.starts_at:
            raise ValidationError("زمان‌بندی آزمون شبانه معتبر نیست.")
        if now < exam.starts_at:
            raise ValidationError("زمان شروع آزمون فرا نرسیده است.")
        if now >= exam.ends_at:
            raise ValidationError("مهلت آزمون شبانه به پایان رسیده است.")
        shared_deadline = min(
            exam.starts_at + timedelta(minutes=exam.duration_minutes),
            exam.ends_at,
        )
    else:
        if exam.starts_at and now < exam.starts_at:
            raise ValidationError("زمان شروع آزمون فرا نرسیده است.")
        # Other scheduled exams retain their shared start/deadline behavior.
        if exam.starts_at:
            shared_deadline = exam.starts_at + timedelta(minutes=exam.duration_minutes)
            if exam.ends_at:
                shared_deadline = min(shared_deadline, exam.ends_at)
            if now >= shared_deadline:
                raise ValidationError("مهلت شرکت در این آزمون به پایان رسیده است.")
        else:
            shared_deadline = None
            if exam.ends_at and now >= exam.ends_at:
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
        if existing.deadline_at > now:
            return existing, False
        finalize_attempt(existing.pk, user)
        if is_night and now >= shared_deadline:
            return existing, True
    if is_night and now >= shared_deadline:
        return None, True
    if not is_night and ExamAttempt.objects.filter(exam=exam, user=user).count() >= exam.max_attempts:
        raise ValidationError("تعداد دفعات مجاز شرکت در آزمون تمام شده است.")
    started_at = now if is_night else (exam.starts_at if exam.starts_at else now)
    deadline_at = shared_deadline or (now + timedelta(minutes=exam.duration_minutes))
    if not is_night and not exam.starts_at and exam.ends_at:
        deadline_at = min(deadline_at, exam.ends_at)
    attempt = ExamAttempt.objects.create(
        exam=exam, user=user, started_at=started_at, deadline_at=deadline_at,
    )
    items = list(
        exam.exam_questions.select_related("question")
        .prefetch_related("question__options").all()
    )
    rng = random.SystemRandom()
    rng.shuffle(items)
    for position, item in enumerate(items, start=1):
        _build_attempt_question(attempt, item, rng, position)
    return attempt, False


@transaction.atomic
def save_answer(attempt_id, question_id, option_id, user):
    attempt = ExamAttempt.objects.select_for_update().get(pk=attempt_id, user=user)
    if attempt.status != ExamAttempt.Status.IN_PROGRESS:
        raise ValidationError("این تلاش آزمون فعال نیست.")
    if timezone.now() >= attempt.deadline_at:
        raise ValidationError("زمان پاسخ‌گویی به پایان رسیده است.")
    try:
        question = AttemptQuestion.objects.get(pk=question_id, attempt=attempt)
        option = AttemptOption.objects.get(pk=option_id, attempt_question=question)
    except (AttemptQuestion.DoesNotExist, AttemptOption.DoesNotExist):
        raise ValidationError("سؤال یا گزینه انتخاب‌شده متعلق به این آزمون نیست.")
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
    if now < attempt.deadline_at and attempt.exam.starts_at and attempt.exam.kind != Exam.Kind.NIGHT:
        raise ValidationError("تحویل آزمون سراسری پیش از زمان پایان مجاز نیست.")
    # Unscheduled practice exams may be submitted early.
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
    if attempt.exam.kind == Exam.Kind.NIGHT and attempt.exam.counts_for_league:
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
            "attempt_id": str(attempt.pk), "exam_id": str(attempt.exam_id),
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
    if exam.counts_for_league and exam.kind != Exam.Kind.NIGHT:
        raise ValidationError("فقط آزمون شبانه می‌تواند در رتبه‌بندی لیگ اثر بگذارد.")
    if exam.kind == Exam.Kind.NIGHT:
        if not exam.counts_for_league:
            raise ValidationError("آزمون شبانه رسمی باید در رتبه‌بندی لیگ محاسبه شود.")
        if exam.requires_purchase:
            raise ValidationError("آزمون شبانه باید رایگان باشد.")
        if not exam.starts_at or not exam.ends_at or exam.ends_at <= exam.starts_at:
            raise ValidationError("برای انتشار آزمون شبانه، زمان شروع و پایان معتبر الزامی است.")
    items = list(exam.exam_questions.select_related("question").prefetch_related("question__options"))
    if exam.kind == Exam.Kind.NIGHT:
        question_ids = [item.question_id for item in items]
        # Serialize publication of overlapping source questions to prevent
        # concurrent admins from publishing the same question in two night exams.
        from apps.questions.models import Question
        list(
            Question.objects.select_for_update()
            .filter(pk__in=question_ids)
            .order_by("pk")
            .values_list("pk", flat=True)
        )
        reused = ExamQuestion.objects.filter(
            question_id__in=question_ids,
            exam__kind=Exam.Kind.NIGHT,
            exam__status__in=[Exam.Status.PUBLISHED, Exam.Status.ARCHIVED],
        ).exclude(exam=exam).exists()
        if reused:
            raise ValidationError("سؤال استفاده‌شده در آزمون شبانه منتشرشده، دوباره قابل انتشار نیست.")
    if not items:
        raise ValidationError("برای انتشار، آزمون باید حداقل یک سؤال داشته باشد.")

    # Exam time is derived from its question count: exactly one minute per question.
    question_count = len(items)
    if question_count > 65535:
        raise ValidationError("تعداد سؤال‌های آزمون از سقف مجاز بیشتر است.")
    calculated_duration = question_count
    if exam.starts_at and exam.ends_at:
        required_end = exam.starts_at + timedelta(minutes=calculated_duration)
        if exam.kind != Exam.Kind.NIGHT and exam.ends_at < required_end:
            raise ValidationError(
                "زمان پایان آزمون برای اختصاص یک دقیقه به هر سؤال کافی نیست."
            )

    for item in items:
        if exam.kind == Exam.Kind.NIGHT:
            if item.question.status == item.question.Status.REJECTED:
                raise ValidationError("سؤال ردشده قابل استفاده در آزمون شبانه نیست.")
        elif item.question.status != item.question.Status.PUBLISHED:
            raise ValidationError("همه سؤال‌های آزمون باید منتشرشده باشند.")
        if item.question.options.count() != 4 or item.question.options.filter(is_correct=True).count() != 1:
            raise ValidationError("هر سؤال باید چهار گزینه و دقیقاً یک پاسخ صحیح داشته باشد.")
    exam.duration_minutes = calculated_duration
    if exam.kind == Exam.Kind.NIGHT:
        # The official night exam has one shared window for everyone.
        exam.ends_at = exam.starts_at + timedelta(minutes=calculated_duration)
    exam.status = Exam.Status.PUBLISHED
    exam.save(update_fields=["duration_minutes", "ends_at", "status"])
    return exam
