import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.exams.models import AttemptOption, Exam, ExamQuestion
from apps.questions.models import Question, QuestionOption
from apps.questions.services import publish_question, review_question, submit_for_review, verify_question_source


@pytest.mark.django_db
def test_participant_can_start_answer_resume_and_finalize_exam_through_api():
    user = get_user_model().objects.create_user(phone_number="09127770001")
    question = Question.objects.create(
        subject=Question.Subject.DIRECT_TAX,
        difficulty=Question.Difficulty.HARD,
        prompt="نرخ نمونه چقدر است؟",
        explanation="پاسخ تشریحی آزمون آزمایشی.",
        source_reference="قانون آزمایشی، ماده ۱",
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
    reviewer = get_user_model().objects.create_user(phone_number="09127770002")
    submit_for_review(question.pk, user)
    review_question(question.pk, reviewer, True)
    verify_question_source(question.pk, reviewer)
    publish_question(question.pk)
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

    correct_snapshot_option = AttemptOption.objects.get(
        attempt_question_id=question_data["id"], source_option_id=correct.pk,
    )
    answered = client.post(
        reverse("attempt-answer", args=[attempt_id]),
        {"question_id": question_data["id"], "option_id": correct_snapshot_option.pk},
        format="json",
    )
    assert answered.status_code == 200

    resumed = client.post(reverse("exam-start", args=[exam.pk]), {}, format="json")
    assert resumed.data["id"] == attempt_id
    assert resumed.data["questions"][0]["selected_option_id"] == correct_snapshot_option.pk

    result = client.post(reverse("attempt-finalize", args=[attempt_id]), {}, format="json")
    assert result.status_code == 200
    assert result.data["score"] == 10
    assert result.data["correct_count"] == 1
    assert result.data["wrong_count"] == 0


@pytest.mark.django_db
def test_nightly_exam_submission_updates_national_and_verified_provincial_leaderboards():
    from datetime import timedelta
    from django.utils import timezone
    from apps.league.models import LeagueSeason, LeagueScoreEntry

    user = get_user_model().objects.create_user(
        phone_number="09127770009",
        display_name="شرکت‌کننده شبانه",
        province="خوزستان",
        province_verified=True,
    )
    now = timezone.now()
    season = LeagueSeason.objects.create(
        title="فصل آزمون یکپارچه",
        starts_at=now - timedelta(days=1),
        ends_at=now + timedelta(days=1),
        status=LeagueSeason.Status.ACTIVE,
    )
    question = Question.objects.create(
        subject=Question.Subject.VAT,
        difficulty=Question.Difficulty.HARD,
        prompt="در سناریوی آزمایشی، پاسخ صحیح کدام است؟",
        explanation="تشریح پاسخ آزمون شبانه.",
        source_reference="قانون مالیات بر ارزش افزوده، ماده ۲؛ مرجع آزمایشی",
        author=user,
    )
    correct = QuestionOption.objects.create(
        question=question, position=1, text="پاسخ صحیح", is_correct=True,
    )
    for position, option_text in enumerate(("گزینه دوم", "گزینه سوم", "گزینه چهارم"), start=2):
        QuestionOption.objects.create(
            question=question, position=position, text=option_text, is_correct=False,
        )
    reviewer = get_user_model().objects.create_user(phone_number="09127770002")
    submit_for_review(question.pk, user)
    review_question(question.pk, reviewer, True)
    verify_question_source(question.pk, reviewer)
    publish_question(question.pk)
    exam = Exam.objects.create(
        title="آزمون شبانه یکپارچه",
        kind=Exam.Kind.NIGHTLY,
        duration_minutes=20,
        max_attempts=1,
        counts_for_league=True,
    )
    ExamQuestion.objects.create(
        exam=exam, question=question, position=1, points_correct=10, points_wrong=-3,
    )
    exam.status = Exam.Status.PUBLISHED
    exam.save(update_fields=["status"])

    client = APIClient()
    client.force_authenticate(user=user)
    started = client.post(reverse("exam-start", args=[exam.pk]), {}, format="json")
    assert started.status_code == 200
    attempt_id = started.data["id"]
    snapshot = started.data["questions"][0]
    correct_snapshot_option = AttemptOption.objects.get(
        attempt_question_id=snapshot["id"], source_option_id=correct.pk,
    )
    answered = client.post(
        reverse("attempt-answer", args=[attempt_id]),
        {"question_id": snapshot["id"], "option_id": correct_snapshot_option.pk},
        format="json",
    )
    assert answered.status_code == 200

    finalized = client.post(reverse("attempt-finalize", args=[attempt_id]), {}, format="json")
    assert finalized.status_code == 200
    assert finalized.data["score"] == 10
    assert LeagueScoreEntry.objects.filter(attempt_id=attempt_id, season=season).count() == 1

    national = client.get("/api/v1/league/leaderboard/")
    provincial = client.get("/api/v1/league/provincial-leaderboard/")
    assert national.status_code == 200
    assert national.data["results"][0]["total_score"] == 10
    assert provincial.status_code == 200
    assert provincial.data["verified"] is True
    assert provincial.data["province"] == "خوزستان"
    assert provincial.data["results"][0]["total_score"] == 10
