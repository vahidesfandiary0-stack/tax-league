import random

import pytest
from django.contrib.auth import get_user_model

from apps.exams.models import Exam, ExamAttempt, ExamQuestion
from apps.exams.services import start_attempt
from apps.questions.models import Question, QuestionOption


@pytest.mark.django_db
def test_each_participant_gets_independent_question_option_order_and_numeric_values(monkeypatch):
    user_model = get_user_model()
    author = user_model.objects.create_user(phone_number="09120000101")
    first = user_model.objects.create_user(phone_number="09120000102")
    second = user_model.objects.create_user(phone_number="09120000103")
    exam = Exam.objects.create(
        title="آزمون نسخه‌های متفاوت", kind=Exam.Kind.MOCK, duration_minutes=30,
    )
    source_questions = []
    for index in range(5):
        question = Question.objects.create(
            subject=Question.Subject.DIRECT_TAX,
            prompt=f"اگر مبلغ {{amount}} باشد، سؤال {index}؟",
            variant_config={"variables": {"amount": {"min": 100, "max": 900, "step": 100}}},
            author=author,
        )
        for position in range(1, 5):
            QuestionOption.objects.create(
                question=question,
                position=position,
                text=f"مبلغ {{amount}} - گزینه {position}",
                is_correct=(position == 2),
            )
        question.status = Question.Status.PUBLISHED
        question.save(update_fields=["status"])
        ExamQuestion.objects.create(exam=exam, question=question, position=index + 1)
        source_questions.append(question)
    exam.status = Exam.Status.PUBLISHED
    exam.save(update_fields=["status"])

    monkeypatch.setattr("apps.exams.services.random.SystemRandom", lambda: random.Random(11))
    first_attempt = start_attempt(exam.pk, first)
    monkeypatch.setattr("apps.exams.services.random.SystemRandom", lambda: random.Random(22))
    second_attempt = start_attempt(exam.pk, second)

    first_questions = list(first_attempt.questions.order_by("position"))
    second_questions = list(second_attempt.questions.order_by("position"))
    assert [q.source_question_id for q in first_questions] != [
        q.source_question_id for q in second_questions
    ]
    assert {q.source_question_id for q in first_questions} == {q.pk for q in source_questions}
    assert {q.source_question_id for q in second_questions} == {q.pk for q in source_questions}

    for attempt_questions in (first_questions, second_questions):
        for question in attempt_questions:
            options = list(question.options.order_by("position"))
            assert len(options) == 4
            assert sum(option.is_correct for option in options) == 1
            assert len({option.text for option in options}) == 4
            displayed_amount = int(question.prompt.split("اگر مبلغ ")[1].split(" باشد")[0])
            assert 100 <= displayed_amount <= 900 and displayed_amount % 100 == 0
            assert all(str(displayed_amount) in option.text for option in options)

    first_amounts = [int(q.prompt.split("اگر مبلغ ")[1].split(" باشد")[0]) for q in first_questions]
    second_amounts = [int(q.prompt.split("اگر مبلغ ")[1].split(" باشد")[0]) for q in second_questions]
    assert first_amounts != second_amounts
