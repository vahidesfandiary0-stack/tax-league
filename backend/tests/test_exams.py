from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.exams.models import (
    AttemptAnswer, Exam, ExamAttempt, ExamQuestion,
)
from apps.exams.services import finalize_attempt, save_answer, start_attempt
from apps.exams.serializers import AttemptSerializer
from apps.notifications.models import Notification
from apps.questions.models import Question, QuestionOption


@pytest.mark.django_db
def make_published_exam(user, *, question_count=1, ends_at=None, kind=Exam.Kind.DAILY, max_attempts=2, counts_for_league=False):
    questions = []
    for index in range(question_count):
        question = Question.objects.create(
            subject=Question.Subject.DIRECT_TAX,
            prompt=f"سؤال آزمایشی {index + 1}",
            author=user,
        )
        QuestionOption.objects.create(
            question=question, position=1, text="پاسخ صحیح", is_correct=True
        )
        QuestionOption.objects.create(
            question=question, position=2, text="پاسخ نادرست", is_correct=False
        )
        question.status = Question.Status.PUBLISHED
        question.save(update_fields=["status"])
        questions.append(question)

    exam = Exam.objects.create(
        title="آزمون آزمایشی",
        kind=kind,
        duration_minutes=30,
        max_attempts=max_attempts,
        counts_for_league=counts_for_league,
        ends_at=ends_at,
    )
    for position, question in enumerate(questions, start=1):
        ExamQuestion.objects.create(
            exam=exam, question=question, position=position,
            points_correct=10, points_wrong=-3,
        )
    exam.status = Exam.Status.PUBLISHED
    exam.save(update_fields=["status"])
    return exam


@pytest.mark.django_db
def test_attempt_deadline_never_exceeds_exam_closing_time():
    user = get_user_model().objects.create_user(phone_number="09123330001")
    close_time = timezone.now() + timedelta(minutes=10)
    exam = make_published_exam(user, ends_at=close_time)

    attempt = start_attempt(exam.pk, user)

    assert attempt.deadline_at <= close_time
    assert attempt.deadline_at > attempt.started_at


@pytest.mark.django_db
def test_exam_cannot_be_started_at_or_after_closing_time():
    user = get_user_model().objects.create_user(phone_number="09123330002")
    now = timezone.now()
    exam = make_published_exam(user, ends_at=now)

    with patch("apps.exams.services.timezone.now", return_value=now):
        with pytest.raises(DjangoValidationError):
            start_attempt(exam.pk, user)


@pytest.mark.django_db
def test_answer_cannot_use_option_from_another_question():
    user = get_user_model().objects.create_user(phone_number="09123330003")
    exam = make_published_exam(user, question_count=2)
    attempt = start_attempt(exam.pk, user)
    questions = list(attempt.questions.order_by("position"))
    foreign_option = questions[1].options.first()

    with pytest.raises(DjangoValidationError):
        save_answer(attempt.pk, questions[0].pk, foreign_option.pk, user)

    assert not AttemptAnswer.objects.filter(attempt_question=questions[0]).exists()


@pytest.mark.django_db
def test_answer_is_rejected_after_server_deadline():
    user = get_user_model().objects.create_user(phone_number="09123330004")
    exam = make_published_exam(user)
    attempt = start_attempt(exam.pk, user)
    attempt.started_at = timezone.now() - timedelta(minutes=10)
    attempt.deadline_at = timezone.now() - timedelta(minutes=1)
    attempt.save(update_fields=["started_at", "deadline_at"])
    question = attempt.questions.first()
    correct_option = question.options.get(is_correct=True)

    with pytest.raises(DjangoValidationError):
        save_answer(attempt.pk, question.pk, correct_option.pk, user)


@pytest.mark.django_db
def test_scoring_is_server_side_and_finalization_is_idempotent():
    user = get_user_model().objects.create_user(phone_number="09123330005")
    exam = make_published_exam(user, question_count=2)
    attempt = start_attempt(exam.pk, user)
    questions = list(attempt.questions.order_by("position"))

    save_answer(
        attempt.pk, questions[0].pk,
        questions[0].options.get(is_correct=True).pk, user,
    )
    save_answer(
        attempt.pk, questions[1].pk,
        questions[1].options.get(is_correct=False).pk, user,
    )

    result = finalize_attempt(attempt.pk, user)
    assert result.status == ExamAttempt.Status.SUBMITTED
    assert result.score == 7
    assert result.correct_count == 1
    assert result.wrong_count == 1
    assert result.blank_count == 0

    second_result = finalize_attempt(attempt.pk, user)
    assert second_result.pk == result.pk
    assert second_result.score == 7
    assert Notification.objects.filter(
        recipient=user, kind=Notification.Kind.EXAM_RESULT
    ).count() == 1


@pytest.mark.django_db
def test_user_cannot_answer_or_finalize_another_users_attempt():
    owner = get_user_model().objects.create_user(phone_number="09123330006")
    stranger = get_user_model().objects.create_user(phone_number="09123330007")
    exam = make_published_exam(owner)
    attempt = start_attempt(exam.pk, owner)
    question = attempt.questions.first()
    option = question.options.first()

    with pytest.raises(ExamAttempt.DoesNotExist):
        save_answer(attempt.pk, question.pk, option.pk, stranger)
    with pytest.raises(ExamAttempt.DoesNotExist):
        finalize_attempt(attempt.pk, stranger)



@pytest.mark.django_db
def test_restarting_active_exam_returns_same_attempt():
    user = get_user_model().objects.create_user(phone_number="09123330008")
    exam = make_published_exam(user)

    first = start_attempt(exam.pk, user)
    second = start_attempt(exam.pk, user)

    assert first.pk == second.pk
    assert ExamAttempt.objects.filter(exam=exam, user=user).count() == 1


@pytest.mark.django_db
def test_attempt_payload_never_exposes_correct_answer_flag():
    user = get_user_model().objects.create_user(phone_number="09123330009")
    exam = make_published_exam(user)
    attempt = start_attempt(exam.pk, user)

    payload = AttemptSerializer(attempt).data
    for question in payload["questions"]:
        for option in question["options"]:
            assert "is_correct" not in option
    assert "explanation" not in payload["questions"][0]


@pytest.mark.django_db
def test_finalization_after_deadline_marks_attempt_expired():
    user = get_user_model().objects.create_user(phone_number="09123330010")
    exam = make_published_exam(user)
    attempt = start_attempt(exam.pk, user)
    attempt.started_at = timezone.now() - timedelta(minutes=10)
    attempt.deadline_at = timezone.now() - timedelta(minutes=1)
    attempt.save(update_fields=["started_at", "deadline_at"])

    result = finalize_attempt(attempt.pk, user)

    assert result.status == ExamAttempt.Status.EXPIRED
    assert result.submitted_at is not None



@pytest.mark.django_db
def test_night_exam_allows_unlimited_attempts():
    user = get_user_model().objects.create_user(phone_number="09123330101")
    exam = make_published_exam(
        user, kind=Exam.Kind.NIGHT, max_attempts=0, counts_for_league=True
    )

    attempts = []
    for _ in range(3):
        attempt = start_attempt(exam.pk, user)
        attempts.append(attempt.pk)
        result = finalize_attempt(attempt.pk, user)
        assert result.status == ExamAttempt.Status.SUBMITTED

    assert len(set(attempts)) == 3
    assert ExamAttempt.objects.filter(exam=exam, user=user).count() == 3



@pytest.mark.django_db
def test_manager_can_publish_exam_with_unreviewed_question_and_start_it_immediately():
    from apps.exams.services import publish_exam

    manager = get_user_model().objects.create_superuser(
        phone_number="09123330102", password="unused"
    )
    question = Question.objects.create(
        subject=Question.Subject.VAT,
        prompt="سؤال مدیریتی راستی‌آزمایی‌نشده",
        explanation="توضیح آزمایشی",
        author=manager,
        status=Question.Status.DRAFT,
    )
    for position in range(1, 5):
        QuestionOption.objects.create(
            question=question,
            position=position,
            text=f"گزینه {position}",
            is_correct=(position == 2),
        )
    future_start = timezone.now() + timedelta(days=30)
    exam = Exam.objects.create(
        title="شبانه فوری با سؤال پیش‌نویس",
        kind=Exam.Kind.NIGHT,
        duration_minutes=20,
        max_attempts=0,
        starts_at=future_start,
        ends_at=None,
        counts_for_league=True,
        requires_purchase=False,
    )
    ExamQuestion.objects.create(exam=exam, question=question, position=1)

    published = publish_exam(exam.pk)
    attempt = start_attempt(published.pk, manager)

    assert published.status == Exam.Status.PUBLISHED
    assert question.status == Question.Status.DRAFT
    assert attempt.started_at <= timezone.now()
    assert attempt.deadline_at > attempt.started_at
    assert attempt.questions.count() == 1


@pytest.mark.django_db
def test_manager_can_publish_non_night_exam_with_unreviewed_question_but_it_is_not_league_exam():
    from apps.exams.services import publish_exam
    from apps.league.services import record_attempt_score
    from apps.league.models import LeagueScoreEntry, LeagueSeason

    manager = get_user_model().objects.create_superuser(
        phone_number="09123330103", password="unused"
    )
    season = LeagueSeason.objects.create(
        title="فصل آزمون مدیریتی",
        starts_at=timezone.now() - timedelta(days=1),
        ends_at=timezone.now() + timedelta(days=1),
        status=LeagueSeason.Status.ACTIVE,
    )
    question = Question.objects.create(
        subject=Question.Subject.DIRECT_TAX,
        prompt="سؤال تمرینی تأییدنشده",
        author=manager,
        status=Question.Status.PENDING,
    )
    for position in range(1, 5):
        QuestionOption.objects.create(
            question=question,
            position=position,
            text=f"گزینه {position}",
            is_correct=(position == 1),
        )
    exam = Exam.objects.create(
        title="آزمون تمرینی مدیریتی",
        kind=Exam.Kind.DAILY,
        duration_minutes=15,
        max_attempts=1,
        counts_for_league=False,
    )
    ExamQuestion.objects.create(exam=exam, question=question, position=1)

    published = publish_exam(exam.pk)
    attempt = start_attempt(published.pk, manager)
    result = finalize_attempt(attempt.pk, manager)

    assert result.status == ExamAttempt.Status.SUBMITTED
    assert record_attempt_score(attempt.pk) is None
    assert not LeagueScoreEntry.objects.filter(attempt=attempt).exists()
