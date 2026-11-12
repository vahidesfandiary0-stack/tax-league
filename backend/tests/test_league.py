from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.test import APIClient

from apps.exams.models import Exam, ExamAttempt
from apps.league.models import LeagueScoreAdjustment, LeagueScoreEntry, LeagueSeason, LeagueSeasonEvent
from apps.league.services import activate_season, adjust_score, close_season, record_attempt_score


def make_season(title="فصل آزمایشی", *, starts_at=None, ends_at=None):
    now = timezone.now()
    return LeagueSeason.objects.create(
        title=title,
        starts_at=starts_at or now - timedelta(days=1),
        ends_at=ends_at or now + timedelta(days=1),
    )


def make_official_attempt(user, *, submitted_at=None, score=17):
    now = submitted_at or timezone.now()
    exam = Exam.objects.create(
        title="آزمون رسمی", kind=Exam.Kind.DAILY,
        duration_minutes=30, max_attempts=1, counts_for_league=True,
    )
    return ExamAttempt.objects.create(
        exam=exam, user=user, status=ExamAttempt.Status.SUBMITTED,
        started_at=now - timedelta(minutes=10),
        deadline_at=now + timedelta(minutes=20),
        submitted_at=now, score=score, correct_count=2,
        wrong_count=1, blank_count=0,
    )


@pytest.mark.django_db
def test_season_activation_and_closure_create_immutable_audit_events():
    user = get_user_model().objects.create_user(phone_number="09124440001")
    season = make_season()

    active = activate_season(season.pk, user, note="شروع رسمی")
    assert active.status == LeagueSeason.Status.ACTIVE
    assert active.events.count() == 1
    assert active.events.first().kind == LeagueSeasonEvent.Kind.ACTIVATED

    with patch("apps.league.services.timezone.now", return_value=season.ends_at + timedelta(seconds=1)):
        closed = close_season(season.pk, user, note="پایان فصل")
    assert closed.status == LeagueSeason.Status.CLOSED
    assert closed.events.count() == 2
    assert list(closed.events.values_list("kind", flat=True)) == [
        LeagueSeasonEvent.Kind.ACTIVATED, LeagueSeasonEvent.Kind.CLOSED
    ]


@pytest.mark.django_db
def test_season_cannot_activate_before_start_or_close_early():
    user = get_user_model().objects.create_user(phone_number="09124440002")
    future = make_season(
        "فصل آینده",
        starts_at=timezone.now() + timedelta(days=1),
        ends_at=timezone.now() + timedelta(days=2),
    )
    with pytest.raises(ValidationError):
        activate_season(future.pk, user)

    active = make_season("فصل جاری")
    activate_season(active.pk, user)
    with pytest.raises(ValidationError):
        close_season(active.pk, user)


@pytest.mark.django_db
def test_database_allows_only_one_active_season():
    first = make_season("اول")
    second = make_season("دوم")
    LeagueSeason.objects.filter(pk=first.pk).update(status=LeagueSeason.Status.ACTIVE)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            LeagueSeason.objects.filter(pk=second.pk).update(
                status=LeagueSeason.Status.ACTIVE
            )


@pytest.mark.django_db
def test_record_attempt_score_is_idempotent_and_uses_active_season():
    user = get_user_model().objects.create_user(phone_number="09124440003")
    season = make_season()
    LeagueSeason.objects.filter(pk=season.pk).update(status=LeagueSeason.Status.ACTIVE)
    attempt = make_official_attempt(user)

    first = record_attempt_score(attempt.pk)
    second = record_attempt_score(attempt.pk)

    assert first.pk == second.pk
    assert LeagueScoreEntry.objects.filter(attempt=attempt).count() == 1
    assert first.season_id == season.pk
    assert first.score == 17


@pytest.mark.django_db
def test_score_from_outside_active_season_is_not_added_to_any_season():
    user = get_user_model().objects.create_user(phone_number="09124440004")
    attempt = make_official_attempt(user)

    assert record_attempt_score(attempt.pk) is None
    assert not LeagueScoreEntry.objects.filter(attempt=attempt).exists()


@pytest.mark.django_db
def test_my_stats_can_read_closed_season_history():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        phone_number="09124440005", display_name="شرکت‌کننده"
    )
    season = make_season("فصل بایگانی")
    LeagueSeason.objects.filter(pk=season.pk).update(status=LeagueSeason.Status.CLOSED)
    attempt = make_official_attempt(user)
    LeagueScoreEntry.objects.create(
        season=season, attempt=attempt, user=user, score=17,
        correct_count=2, wrong_count=1, elapsed_seconds=600,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f"/api/v1/league/me/?season={season.pk}")

    assert response.status_code == 200
    assert response.data["season"]["status"] == LeagueSeason.Status.CLOSED
    assert response.data["rank"] == 1
    assert response.data["total_score"] == 17
    assert response.data["exams_count"] == 1


@pytest.mark.django_db
def test_leaderboard_limit_is_validated():
    user = get_user_model().objects.create_user(phone_number="09124440006")
    season = make_season()
    LeagueSeason.objects.filter(pk=season.pk).update(status=LeagueSeason.Status.ACTIVE)
    client = APIClient()
    client.force_authenticate(user=user)

    invalid = client.get("/api/v1/league/leaderboard/?limit=10000")
    malformed = client.get("/api/v1/league/leaderboard/?limit=abc")

    assert invalid.status_code == 400
    assert malformed.status_code == 400



@pytest.mark.django_db
def test_score_ledger_and_season_events_are_immutable():
    user = get_user_model().objects.create_user(phone_number="09124440007")
    season = make_season()
    activate_season(season.pk, user)
    event = season.events.first()

    event.note = "دستکاری سابقه"
    with pytest.raises(ValidationError):
        event.save()
    with pytest.raises(ValidationError):
        LeagueSeasonEvent.objects.filter(pk=event.pk).update(note="تغییر گروهی")
    with pytest.raises(ValidationError):
        LeagueSeasonEvent.objects.filter(pk=event.pk).delete()

    attempt = make_official_attempt(user)
    entry = LeagueScoreEntry.objects.create(
        season=season, attempt=attempt, user=user, score=17,
        correct_count=2, wrong_count=1, elapsed_seconds=600,
    )
    entry.score = 999
    with pytest.raises(ValidationError):
        entry.save()
    with pytest.raises(ValidationError):
        entry.delete()
    with pytest.raises(ValidationError):
        LeagueScoreEntry.objects.filter(pk=entry.pk).update(score=1000)
    with pytest.raises(ValidationError):
        LeagueScoreEntry.objects.filter(pk=entry.pk).delete()



@pytest.mark.django_db
def test_season_status_cannot_be_changed_through_regular_model_save():
    season = make_season("فصل فقط پیش‌نویس")
    season.status = LeagueSeason.Status.ACTIVE

    with pytest.raises(ValidationError):
        season.save()


@pytest.mark.django_db
def test_closed_season_score_correction_is_append_only_and_idempotent():
    from uuid import uuid4

    user = get_user_model().objects.create_user(phone_number="09124440008")
    manager = get_user_model().objects.create_superuser(
        phone_number="09124440009", password="not-used"
    )
    season = make_season("فصل اصلاح امتیاز")
    activate_season(season.pk, manager)
    attempt = make_official_attempt(user)
    entry = LeagueScoreEntry.objects.create(
        season=season, attempt=attempt, user=user, score=17,
        correct_count=2, wrong_count=1, elapsed_seconds=600,
    )
    with patch("apps.league.services.timezone.now", return_value=season.ends_at + timedelta(seconds=1)):
        close_season(season.pk, manager)
    key = uuid4()
    first = adjust_score(entry.pk, manager, 3, "اصلاح نتیجه بررسی‌شده", key)
    second = adjust_score(entry.pk, manager, 3, "اصلاح نتیجه بررسی‌شده", key)
    assert first.pk == second.pk
    assert LeagueScoreAdjustment.objects.filter(entry=entry).count() == 1
    client = APIClient()
    client.force_authenticate(user=user)
    stats = client.get(f"/api/v1/league/me/?season={season.pk}")
    assert stats.data["total_score"] == 20
    assert stats.data["rank"] == 1
    board = client.get(f"/api/v1/league/leaderboard/?season={season.pk}")
    assert board.status_code == 200
    assert board.data["results"][0]["total_score"] == 20
    assert entry.score == 17
    with pytest.raises(ValidationError):
        first.delete()


@pytest.mark.django_db
def test_score_correction_requires_closed_season_and_reason():
    from uuid import uuid4

    user = get_user_model().objects.create_user(phone_number="09124440010")
    manager = get_user_model().objects.create_superuser(
        phone_number="09124440011", password="not-used"
    )
    season = make_season("فصل هنوز فعال")
    activate_season(season.pk, manager)
    attempt = make_official_attempt(user)
    entry = LeagueScoreEntry.objects.create(
        season=season, attempt=attempt, user=user, score=17,
        correct_count=2, wrong_count=1, elapsed_seconds=600,
    )
    with pytest.raises(ValidationError):
        adjust_score(entry.pk, manager, 2, "اصلاح", uuid4())


@pytest.mark.django_db
def test_score_correction_rejects_non_manager_and_reused_key_with_different_payload():
    from uuid import uuid4

    user = get_user_model().objects.create_user(phone_number="09124440012")
    manager = get_user_model().objects.create_superuser(
        phone_number="09124440013", password="not-used"
    )
    season = make_season("فصل کنترل اصلاح")
    activate_season(season.pk, manager)
    attempt = make_official_attempt(user)
    entry = LeagueScoreEntry.objects.create(
        season=season, attempt=attempt, user=user, score=17,
        correct_count=2, wrong_count=1, elapsed_seconds=600,
    )
    with patch("apps.league.services.timezone.now", return_value=season.ends_at + timedelta(seconds=1)):
        close_season(season.pk, manager)
    with pytest.raises(ValidationError):
        adjust_score(entry.pk, user, 1, "بدون مجوز", uuid4())

    key = uuid4()
    adjust_score(entry.pk, manager, 1, "اصلاح معتبر", key)
    with pytest.raises(ValidationError):
        adjust_score(entry.pk, manager, 2, "اصلاح متفاوت", key)
