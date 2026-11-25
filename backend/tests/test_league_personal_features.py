from datetime import timedelta
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from apps.exams.models import Exam, ExamAttempt
from apps.league.models import LeagueScoreEntry, LeagueSeason
from apps.subscriptions.models import SubscriptionPlan, UserSubscription


@pytest.mark.django_db
def test_latest_night_leaderboard_and_top_five_are_free_and_use_night_ledger():
    User = get_user_model()
    first = User.objects.create_user(phone_number="09120000101", display_name="نفر اول")
    second = User.objects.create_user(phone_number="09120000102", display_name="نفر دوم")
    season = LeagueSeason.objects.create(title="فصل تست", starts_at=timezone.now()-timedelta(days=1),
        ends_at=timezone.now()+timedelta(days=1), status=LeagueSeason.Status.ACTIVE)
    exam = Exam.objects.create(title="شبانه اخیر", kind=Exam.Kind.NIGHT, duration_minutes=30,
        max_attempts=0, counts_for_league=True, status=Exam.Status.PUBLISHED,
        starts_at=timezone.now())
    for user, score, correct, wrong, elapsed in [(first,90,9,1,500),(second,80,8,2,400)]:
        attempt = ExamAttempt.objects.create(exam=exam, user=user, status=ExamAttempt.Status.SUBMITTED,
            started_at=timezone.now()-timedelta(minutes=10), deadline_at=timezone.now()+timedelta(minutes=20),
            submitted_at=timezone.now(), score=score, correct_count=correct, wrong_count=wrong, blank_count=0)
        LeagueScoreEntry.objects.create(season=season, attempt=attempt, user=user, score=score,
            correct_count=correct, wrong_count=wrong, elapsed_seconds=elapsed)
    client=APIClient(); client.force_authenticate(user=first)
    board=client.get("/api/v1/league/latest-night/")
    top=client.get("/api/v1/league/me/top-records/")
    assert board.status_code==200 and board.data["results"][0]["display_name"]=="نفر اول"
    assert top.status_code==200 and top.data["total_valid_records"]==1


@pytest.mark.django_db
def test_detailed_performance_requires_active_subscription_and_reports_missing_data():
    user=get_user_model().objects.create_user(phone_number="09120000103")
    client=APIClient(); client.force_authenticate(user=user)
    assert client.get("/api/v1/league/me/performance/").status_code==403
    plan=SubscriptionPlan.objects.get(period=SubscriptionPlan.Period.MONTHLY)
    from apps.payments.models import PaymentOrder
    order=PaymentOrder.objects.create(user=user, product_type=PaymentOrder.ProductType.SUBSCRIPTION,
        plan=plan, amount_irr=1000, status=PaymentOrder.Status.APPROVED)
    now=timezone.now()
    UserSubscription.objects.create(user=user, plan=plan, starts_at=now-timedelta(days=1),
        ends_at=now+timedelta(days=29), source_order=order)
    response=client.get("/api/v1/league/me/performance/")
    assert response.status_code==200 and response.data["data_available"] is False


@pytest.mark.django_db
def test_latest_night_leaderboard_ignores_a_future_published_exam():
    user = get_user_model().objects.create_user(
        phone_number="09120000104", display_name="شرکت‌کننده"
    )
    now = timezone.now()
    season = LeagueSeason.objects.create(
        title="فصل آزمون‌های اخیر",
        starts_at=now - timedelta(days=2),
        ends_at=now + timedelta(days=2),
        status=LeagueSeason.Status.ACTIVE,
    )
    previous_start = now - timedelta(hours=2)
    previous = Exam.objects.create(
        title="آخرین آزمون شروع‌شده",
        kind=Exam.Kind.NIGHT,
        duration_minutes=30,
        max_attempts=0,
        counts_for_league=True,
        status=Exam.Status.ARCHIVED,
        starts_at=previous_start,
        ends_at=previous_start + timedelta(minutes=30),
    )
    attempt = ExamAttempt.objects.create(
        exam=previous,
        user=user,
        status=ExamAttempt.Status.SUBMITTED,
        started_at=previous_start + timedelta(minutes=2),
        deadline_at=previous.ends_at,
        submitted_at=previous.ends_at,
        score=25,
        correct_count=3,
        wrong_count=1,
        blank_count=0,
    )
    LeagueScoreEntry.objects.create(
        season=season,
        attempt=attempt,
        user=user,
        score=25,
        correct_count=3,
        wrong_count=1,
        elapsed_seconds=28 * 60,
    )
    ongoing_start = now - timedelta(minutes=10)
    Exam.objects.create(
        title="آزمون در حال برگزاری",
        kind=Exam.Kind.NIGHT,
        duration_minutes=30,
        max_attempts=0,
        counts_for_league=True,
        status=Exam.Status.PUBLISHED,
        starts_at=ongoing_start,
        ends_at=ongoing_start + timedelta(minutes=20),
    )
    future_start = now + timedelta(hours=2)
    Exam.objects.create(
        title="آزمون آینده",
        kind=Exam.Kind.NIGHT,
        duration_minutes=30,
        max_attempts=0,
        counts_for_league=True,
        status=Exam.Status.PUBLISHED,
        starts_at=future_start,
        ends_at=future_start + timedelta(minutes=30),
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/league/latest-night/")

    assert response.status_code == 200
    assert response.data["exam"]["title"] == "آخرین آزمون شروع‌شده"
    assert response.data["results"][0]["score"] == 25
