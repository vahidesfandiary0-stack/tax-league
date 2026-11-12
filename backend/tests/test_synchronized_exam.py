import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.exams.models import Exam, ExamAttempt, ExamQuestion
from apps.exams.services import finalize_attempt, start_attempt
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

    scheduled_start = timezone.now() - timezone.timedelta(minutes=2)
    exam = Exam.objects.create(
        title="آزمون سراسری", kind=Exam.Kind.WEEKLY, duration_minutes=30,
        starts_at=scheduled_start, ends_at=scheduled_start + timezone.timedelta(minutes=30),
    )
    ExamQuestion.objects.create(exam=exam, question=question, position=1)
    exam.status = Exam.Status.PUBLISHED
    exam.save(update_fields=["status"])

    first_now = scheduled_start + timezone.timedelta(minutes=2)
    monkeypatch.setattr("apps.exams.services.timezone.now", lambda: first_now)
    first_attempt = start_attempt(exam.pk, first)

    later_now = scheduled_start + timezone.timedelta(minutes=12)
    monkeypatch.setattr("apps.exams.services.timezone.now", lambda: later_now)
    second_attempt = start_attempt(exam.pk, second)

    expected_deadline = scheduled_start + timezone.timedelta(minutes=30)
    assert first_attempt.started_at == scheduled_start
    assert second_attempt.started_at == scheduled_start
    assert first_attempt.deadline_at == expected_deadline
    assert second_attempt.deadline_at == expected_deadline


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
    scheduled_start = timezone.now() - timezone.timedelta(minutes=1)
    exam = Exam.objects.create(
        title="آزمون پایان مشترک", kind=Exam.Kind.WEEKLY, duration_minutes=20,
        starts_at=scheduled_start,
    )
    ExamQuestion.objects.create(exam=exam, question=question, position=1)
    exam.status = Exam.Status.PUBLISHED
    exam.save(update_fields=["status"])
    attempt = start_attempt(exam.pk, participant)

    monkeypatch.setattr(
        "apps.exams.services.timezone.now",
        lambda: scheduled_start + timezone.timedelta(minutes=5),
    )
    with pytest.raises(ValidationError, match="پیش از زمان پایان"):
        finalize_attempt(attempt.pk, participant)
    attempt.refresh_from_db()
    assert attempt.status == ExamAttempt.Status.IN_PROGRESS
