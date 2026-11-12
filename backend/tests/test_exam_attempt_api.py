import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.exams.models import Exam, ExamQuestion
from apps.questions.models import Question, QuestionOption


@pytest.mark.django_db
def test_participant_can_start_answer_resume_and_finalize_exam_through_api():
    user = get_user_model().objects.create_user(phone_number="09127770001")
    question = Question.objects.create(
        subject=Question.Subject.DIRECT_TAX,
        prompt="نرخ نمونه چقدر است؟",
        author=user,
    )
    correct = QuestionOption.objects.create(
        question=question, position=1, text="گزینه الف", is_correct=True,
    )
    QuestionOption.objects.create(
        question=question, position=2, text="گزینه ب", is_correct=False,
    )
    QuestionOption.objects.create(
        question=question, position=3, text="گزینه ج", is_correct=False,
    )
    QuestionOption.objects.create(
        question=question, position=4, text="گزینه د", is_correct=False,
    )
    question.status = Question.Status.PUBLISHED
    question.save(update_fields=["status"])
    exam = Exam.objects.create(
        title="آزمون API", kind=Exam.Kind.DAILY, duration_minutes=20,
        max_attempts=1,
    )
    ExamQuestion.objects.create(
        exam=exam, question=question, position=1,
        points_correct=10, points_wrong=-3,
    )
    exam.status = Exam.Status.PUBLISHED
    exam.save(update_fields=["status"])

    client = APIClient()
    client.force_authenticate(user=user)

    started = client.post(reverse("exam-start", args=[exam.pk]), {}, format="json")
    assert started.status_code == 200
    attempt_id = started.data["id"]
    question_data = started.data["questions"][0]
    assert "is_correct" not in question_data["options"][0]
    assert "explanation" not in question_data

    answered = client.post(
        reverse("attempt-answer", args=[attempt_id]),
        {"question_id": question_data["id"], "option_id": correct.pk},
        format="json",
    )
    assert answered.status_code == 200

    resumed = client.post(reverse("exam-start", args=[exam.pk]), {}, format="json")
    assert resumed.data["id"] == attempt_id
    assert resumed.data["questions"][0]["selected_option_id"] == correct.pk

    result = client.post(reverse("attempt-finalize", args=[attempt_id]), {}, format="json")
    assert result.status_code == 200
    assert result.data["score"] == 10
    assert result.data["correct_count"] == 1
    assert result.data["wrong_count"] == 0
