from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from apps.exams.models import (
    AttemptAnswer, AttemptOption, AttemptQuestion, Exam, ExamAttempt, ExamQuestion,
)
from apps.exams.services import finalize_attempt, save_answer, start_attempt
from apps.notifications.models import Notification
from apps.questions.models import Question, QuestionOption


@pytest.mark.django_db
def make_published_exam(user, *, question_count=1, ends_at=None):
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
        kind=Exam.Kind.DAILY,
        duration_minutes=30,
        max_attempts=2,
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
    close_time = timezone.now() + timedelta(minutes=2)
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
