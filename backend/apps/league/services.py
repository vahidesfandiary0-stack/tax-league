from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.exams.models import ExamAttempt
from .models import LeagueScoreEntry, LeagueSeason, LeagueSeasonEvent


@transaction.atomic
def record_attempt_score(attempt_id):
    attempt = ExamAttempt.objects.select_for_update().select_related("exam", "user").get(pk=attempt_id)
    if attempt.status not in (ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED):
        raise ValidationError("فقط آزمون تحویل‌شده یا منقضی‌شده امتیاز می‌گیرد.")
    if attempt.score is None or attempt.submitted_at is None:
        raise ValidationError("نتیجه آزمون هنوز قطعی نشده است.")
    if not attempt.exam.counts_for_league:
        return None

    existing = LeagueScoreEntry.objects.filter(attempt=attempt).first()
    if existing:
        return existing

    season = LeagueSeason.objects.select_for_update().filter(
        status=LeagueSeason.Status.ACTIVE,
        starts_at__lte=attempt.started_at,
        ends_at__gte=attempt.submitted_at,
    ).first()
    if season is None:
        # A completed exam must remain finalized even if no eligible season is active.
        # It simply does not contribute to an official season leaderboard.
        return None

    elapsed = max(0, int((attempt.submitted_at - attempt.started_at).total_seconds()))
    return LeagueScoreEntry.objects.create(
        season=season,
        attempt=attempt,
        user=attempt.user,
        score=attempt.score,
        correct_count=attempt.correct_count,
        wrong_count=attempt.wrong_count,
        elapsed_seconds=elapsed,
    )



@transaction.atomic
def activate_season(season_id, actor, note=""):
    season = LeagueSeason.objects.select_for_update().get(pk=season_id)
    now = timezone.now()
    if season.status != LeagueSeason.Status.DRAFT:
        raise ValidationError("فقط فصل پیش‌نویس قابل فعال‌سازی است.")
    if not (season.starts_at <= now < season.ends_at):
        raise ValidationError("فصل فقط در بازه زمانی تعریف‌شده قابل فعال‌سازی است.")
    if LeagueSeason.objects.filter(status=LeagueSeason.Status.ACTIVE).exclude(pk=season.pk).exists():
        raise ValidationError("یک فصل فعال دیگر وجود دارد؛ ابتدا آن را ببندید.")
    # QuerySet.update is intentional: the model prevents ordinary edits after activation.
    LeagueSeason.objects.filter(pk=season.pk, status=LeagueSeason.Status.DRAFT).update(
        status=LeagueSeason.Status.ACTIVE
    )
    LeagueSeasonEvent.objects.create(
        season=season, actor=actor, kind=LeagueSeasonEvent.Kind.ACTIVATED, note=note
    )
    season.refresh_from_db()
    return season


@transaction.atomic
def close_season(season_id, actor, note=""):
    season = LeagueSeason.objects.select_for_update().get(pk=season_id)
    now = timezone.now()
    if season.status != LeagueSeason.Status.ACTIVE:
        raise ValidationError("فقط فصل فعال قابل بستن است.")
    if now < season.ends_at:
        raise ValidationError("فصل تا پیش از زمان پایان برنامه‌ریزی‌شده قابل بستن نیست.")
    LeagueSeason.objects.filter(pk=season.pk, status=LeagueSeason.Status.ACTIVE).update(
        status=LeagueSeason.Status.CLOSED
    )
    LeagueSeasonEvent.objects.create(
        season=season, actor=actor, kind=LeagueSeasonEvent.Kind.CLOSED, note=note
    )
    season.refresh_from_db()
    return season

def leaderboard_for_season(season_id, limit=100):
    """Aggregate ledger entries; no client-supplied scores are accepted."""
    from django.db.models import Count, IntegerField, Value
    from django.db.models.functions import Coalesce

    season = LeagueSeason.objects.get(pk=season_id, status__in=[
        LeagueSeason.Status.ACTIVE, LeagueSeason.Status.CLOSED
    ])
    rows = LeagueScoreEntry.objects.filter(season=season).values(
        "user_id", "user__display_name"
    ).annotate(
        total_score=Coalesce(Sum("score"), Value(0), output_field=IntegerField()),
        correct_total=Coalesce(Sum("correct_count"), Value(0), output_field=IntegerField()),
        wrong_total=Coalesce(Sum("wrong_count"), Value(0), output_field=IntegerField()),
        total_time=Coalesce(Sum("elapsed_seconds"), Value(0), output_field=IntegerField()),
        exams_count=Count("id"),
    ).order_by("-total_score", "-correct_total", "wrong_total", "total_time", "user_id")[:limit]
    return season, list(rows)
