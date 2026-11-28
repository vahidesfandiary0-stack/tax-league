import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.exams.models import Exam, ExamAttempt, ExamQuestion
from apps.exams.services import finalize_attempt, publish_exam, start_attempt
from apps.questions.models import Question, QuestionOption


@pytest.mark.django_db
def test_scheduled_exam_gives_every_participant_the_same_server_deadline(monkeypatch):
    user_model = get_user_model()
    owner = user_model.objects.create_user(phone_number="09120000001")
    first = user_model.objects.create_user(phone_number="09120000002")
    second = user_model.objects.create_user(phone_number="09120000003")
    question = Question.objects.create(
        subject=Question.Subject.DIRECT_TAX, prompt="سؤال زمان‌بندی", author=owner,
    )
    for position in range(1, 5):
        QuestionOption.objects.create(
            question=question, position=position, text=f"گزینه {position}",
            is_correct=(position == 1),
        )
    question.status = Question.Status.PUBLISHED
    question.save(update_fields=["status"])

    scheduled_start = timezone.now() - timedelta(seconds=10)
    exam = Exam.objects.create(
        title="آزمون سراسری", kind=Exam.Kind.WEEKLY, duration_minutes=30,
        starts_at=scheduled_start, ends_at=scheduled_start + timezone.timedelta(minutes=30),
    )
    ExamQuestion.objects.create(exam=exam, question=question, position=1)
    publish_exam(exam.pk)

    first_now = scheduled_start + timezone.timedelta(seconds=5)
    monkeypatch.setattr("apps.exams.services.timezone.now", lambda: first_now)
    first_attempt = start_attempt(exam.pk, first)

    later_now = scheduled_start + timezone.timedelta(seconds=25)
    monkeypatch.setattr("apps.exams.services.timezone.now", lambda: later_now)
    second_attempt = start_attempt(exam.pk, second)
    # Repeated starts by the same participant resume the existing attempt.
    repeated_first_attempt = start_attempt(exam.pk, first)

    expected_deadline = scheduled_start + timezone.timedelta(minutes=1)
    assert first_attempt.started_at == scheduled_start
    assert second_attempt.started_at == scheduled_start
    assert first_attempt.deadline_at == expected_deadline
    assert second_attempt.deadline_at == expected_deadline
    assert repeated_first_attempt.pk == first_attempt.pk


@pytest.mark.django_db
def test_scheduled_exam_cannot_be_finalized_before_shared_deadline(monkeypatch):
    user_model = get_user_model()
    owner = user_model.objects.create_user(phone_number="09120000011")
    participant = user_model.objects.create_user(phone_number="09120000012")
    question = Question.objects.create(
        subject=Question.Subject.DIRECT_TAX, prompt="سؤال پایان", author=owner,
    )
    for position in range(1, 5):
        QuestionOption.objects.create(
            question=question, position=position, text=f"گزینه {position}",
            is_correct=(position == 1),
        )
    question.status = Question.Status.PUBLISHED
    question.save(update_fields=["status"])
    scheduled_start = timezone.now() - timezone.timedelta(seconds=10)
    exam = Exam.objects.create(
        title="آزمون پایان مشترک", kind=Exam.Kind.WEEKLY, duration_minutes=20,
        starts_at=scheduled_start,
    )
    ExamQuestion.objects.create(exam=exam, question=question, position=1)
    publish_exam(exam.pk)
    attempt = start_attempt(exam.pk, participant)

    monkeypatch.setattr(
        "apps.exams.services.timezone.now",
        lambda: scheduled_start + timezone.timedelta(seconds=30),
    )
    with pytest.raises(ValidationError, match="پیش از زمان پایان"):
        finalize_attempt(attempt.pk, participant)
    attempt.refresh_from_db()
    assert attempt.status == ExamAttempt.Status.IN_PROGRESS

@pytest.mark.django_db
def test_night_exam_late_joiners_share_the_original_deadline(monkeypatch):
    user_model = get_user_model()
    owner = user_model.objects.create_user(phone_number="09120000021")
    first = user_model.objects.create_user(phone_number="09120000022")
    late = user_model.objects.create_user(phone_number="09120000023")
    question = Question.objects.create(
        subject=Question.Subject.DIRECT_TAX, prompt="سؤال شبانه مشترک", author=owner,
    )
    for position in range(1, 5):
        QuestionOption.objects.create(
            question=question, position=position, text=f"گزینه {position}",
            is_correct=(position == 1),
        )
    question.status = Question.Status.PUBLISHED
    question.save(update_fields=["status"])

    scheduled_start = timezone.now() - timedelta(seconds=10)
    scheduled_end = scheduled_start + timedelta(minutes=45)
    exam = Exam.objects.create(
        title="آزمون شبانه با مهلت مشترک", kind=Exam.Kind.NIGHT,
        duration_minutes=30, starts_at=scheduled_start, ends_at=scheduled_end,
        counts_for_league=True, requires_purchase=False,
    )
    ExamQuestion.objects.create(exam=exam, question=question, position=1)
    publish_exam(exam.pk)

    first_now = scheduled_start + timedelta(seconds=5)
    monkeypatch.setattr("apps.exams.services.timezone.now", lambda: first_now)
    first_attempt = start_attempt(exam.pk, first)

    late_now = scheduled_start + timedelta(seconds=25)
    monkeypatch.setattr("apps.exams.services.timezone.now", lambda: late_now)
    late_attempt = start_attempt(exam.pk, late)

    expected_deadline = scheduled_start + timedelta(minutes=1)
    assert first_attempt.deadline_at == expected_deadline
    assert late_attempt.deadline_at == expected_deadline
    assert late_attempt.started_at == late_now

    after_deadline = scheduled_start + timedelta(seconds=61)
    monkeypatch.setattr("apps.exams.services.timezone.now", lambda: after_deadline)
    too_late = user_model.objects.create_user(phone_number="09120000024")
    with pytest.raises(ValidationError, match="مهلت آزمون شبانه"):
        start_attempt(exam.pk, too_late)

