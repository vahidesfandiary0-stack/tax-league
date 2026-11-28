import uuid

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, OuterRef, Subquery, IntegerField, Value, F
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.exams.models import Exam, ExamAttempt
from .models import LeagueScoreAdjustment, LeagueScoreEntry, LeagueSeason, LeagueSeasonEvent


@transaction.atomic
def record_attempt_score(attempt_id):
    attempt = ExamAttempt.objects.select_for_update().select_related("exam", "user").get(pk=attempt_id)
    if attempt.status not in (ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED):
        raise ValidationError("فقط آزمون تحویل‌شده یا منقضی‌شده امتیاز می‌گیرد.")
    if attempt.score is None or attempt.submitted_at is None:
        raise ValidationError("نتیجه آزمون هنوز قطعی نشده است.")
    if not attempt.exam.counts_for_league or attempt.exam.kind != Exam.Kind.NIGHT:
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

def league_rows_for_season(season_id, province=None):
    """Build the official standings from the best adjusted NIGHT attempt per user and exam."""
    from django.db.models import Count, IntegerField, OuterRef, Subquery, Sum, Value, Window
    from django.db.models.functions import Coalesce, RowNumber

    season = LeagueSeason.objects.get(pk=season_id, status__in=[
        LeagueSeason.Status.ACTIVE, LeagueSeason.Status.CLOSED
    ])
    entries = LeagueScoreEntry.objects.filter(
        season=season,
        attempt__exam__kind=Exam.Kind.NIGHT,
        attempt__exam__counts_for_league=True,
    )
    if province is not None:
        entries = entries.filter(user__province=province, user__province_verified=True)

    adjustment_totals = LeagueScoreAdjustment.objects.filter(
        entry_id=OuterRef("pk")
    ).values("entry_id").annotate(total=Sum("score_delta")).values("total")[:1]

    best_entries = entries.annotate(
        adjustment_total=Coalesce(
            Subquery(adjustment_totals, output_field=IntegerField()),
            Value(0), output_field=IntegerField(),
        )
    ).annotate(
        adjusted_score=F("score") + F("adjustment_total")
    ).annotate(
        best_attempt_rank=Window(
            expression=RowNumber(),
            partition_by=[F("user_id"), F("attempt__exam_id")],
            order_by=[
                F("adjusted_score").desc(),
                F("correct_count").desc(),
                F("wrong_count").asc(),
                F("elapsed_seconds").asc(),
                F("attempt_id").asc(),
            ],
        )
    ).filter(best_attempt_rank=1)

    rows = best_entries.values(
        "season_id", "user_id", "user__display_name"
    ).annotate(
        total_score=Sum("adjusted_score"),
        correct_total=Sum("correct_count"),
        wrong_total=Sum("wrong_count"),
        total_time=Sum("elapsed_seconds"),
        exams_count=Count("id"),
    ).order_by(
        "-total_score", "-correct_total", "wrong_total", "total_time", "user_id"
    )
    return season, list(rows)


def leaderboard_for_season(season_id, limit=100, province=None):
    season, rows = league_rows_for_season(season_id, province=province)
    return season, rows[:limit]


@transaction.atomic
def file_league_appeal(attempt_id, user, reason, details):
    from datetime import timedelta
    from .models import LeagueAppeal

    attempt = ExamAttempt.objects.select_for_update().select_related("exam").get(pk=attempt_id)
    if attempt.user_id != user.pk:
        raise ValidationError("این نتیجه متعلق به شما نیست.")
    if attempt.status not in (ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED):
        raise ValidationError("فقط نتیجه نهایی‌شده قابل اعتراض است.")
    if not attempt.exam.counts_for_league or attempt.exam.kind != Exam.Kind.NIGHT:
        raise ValidationError("فقط نتیجه آزمون شبانه رسمی قابل اعتراض است.")
    if attempt.submitted_at is None or timezone.now() > attempt.submitted_at + timedelta(days=7):
        raise ValidationError("مهلت ثبت اعتراض به پایان رسیده است.")
    reason, details = (reason or "").strip(), (details or "").strip()
    if not reason or not details:
        raise ValidationError("موضوع و شرح اعتراض الزامی است.")
    if hasattr(attempt, "league_appeal"):
        raise ValidationError("برای این نتیجه قبلاً اعتراض ثبت شده است.")
    return LeagueAppeal.objects.create(attempt=attempt, user=user, reason=reason[:200], details=details[:4000])


@transaction.atomic
def review_league_appeal(appeal_id, reviewer, decision, decision_note, score_delta=None):
    from .models import LeagueAppeal

    if not (reviewer.is_superuser or (reviewer.is_staff and reviewer.has_perm("league.change_leagueappeal"))):
        raise ValidationError("اجازه بررسی اعتراض‌های لیگ را ندارید.")
    appeal = LeagueAppeal.objects.select_for_update().select_related("attempt", "user").get(pk=appeal_id)
    if appeal.status != LeagueAppeal.Status.PENDING:
        raise ValidationError("این اعتراض قبلاً تعیین تکلیف شده است.")
    note = (decision_note or "").strip()
    if not note:
        raise ValidationError("ثبت توضیح تصمیم الزامی است.")
    if decision == LeagueAppeal.Status.APPROVED:
        if not isinstance(score_delta, int) or isinstance(score_delta, bool) or score_delta == 0:
            raise ValidationError("برای پذیرش اعتراض، اصلاح امتیاز صحیح و غیرصفر وارد کنید.")
        entry = LeagueScoreEntry.objects.filter(attempt=appeal.attempt).first()
        if entry is None:
            raise ValidationError("برای این نتیجه هنوز رکورد امتیاز رسمی وجود ندارد.")
        adjustment = adjust_score(entry.pk, reviewer, score_delta, f"اعتراض {appeal.pk}: {note}", uuid.uuid4())
        appeal.adjustment, appeal.score_delta, appeal.status = adjustment, score_delta, LeagueAppeal.Status.APPROVED
    elif decision == LeagueAppeal.Status.REJECTED:
        if score_delta not in (None, 0):
            raise ValidationError("برای رد اعتراض نباید اصلاح امتیاز ثبت شود.")
        appeal.status, appeal.score_delta = LeagueAppeal.Status.REJECTED, None
    else:
        raise ValidationError("تصمیم نامعتبر است.")
    LeagueAppeal.objects.filter(pk=appeal.pk, status=LeagueAppeal.Status.PENDING).update(
        status=appeal.status, score_delta=appeal.score_delta, adjustment=appeal.adjustment,
        reviewer=reviewer, decision_note=note, reviewed_at=timezone.now(),
    )
    appeal.refresh_from_db()
    return appeal


@transaction.atomic
def adjust_score(entry_id, actor, score_delta, reason, idempotency_key):
    from .models import LeagueScoreAdjustment

    if not (actor.is_superuser or (
        actor.is_staff and actor.has_perm("league.add_leaguescoreadjustment")
    )):
        raise ValidationError("اجازه اصلاح امتیاز لیگ را ندارید.")
    if not isinstance(score_delta, int) or isinstance(score_delta, bool) or score_delta == 0:
        raise ValidationError("مقدار اصلاح امتیاز باید عدد صحیح و غیرصفر باشد.")
    reason = (reason or "").strip()
    if not reason:
        raise ValidationError("علت اصلاح امتیاز الزامی است.")
    entry = LeagueScoreEntry.objects.select_for_update().select_related("season").get(pk=entry_id)
    if entry.season.status != LeagueSeason.Status.CLOSED:
        raise ValidationError("اصلاح امتیاز فقط پس از بسته‌شدن فصل مجاز است.")
    existing = LeagueScoreAdjustment.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        if existing.entry_id == entry.pk and existing.score_delta == score_delta and existing.reason == reason:
            return existing
        raise ValidationError("کلید تکرار قبلاً برای اصلاح دیگری استفاده شده است.")
    return LeagueScoreAdjustment.objects.create(
        entry=entry, actor=actor, score_delta=score_delta,
        reason=reason[:500], idempotency_key=idempotency_key,
    )


def top_records_for_user(user, limit=5):
    """Return up to five best finalized free official NIGHT results, one per exam."""
    attempts = ExamAttempt.objects.filter(
        user=user,
        exam__kind=Exam.Kind.NIGHT,
        exam__counts_for_league=True,
        exam__requires_purchase=False,
        exam__status__in=[Exam.Status.PUBLISHED, Exam.Status.ARCHIVED],
        status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED],
        score__isnull=False,
        submitted_at__isnull=False,
    ).select_related("exam").order_by("submitted_at", "id")

    best_by_exam = {}
    for attempt in attempts:
        adjusted_score = attempt.score
        try:
            adjusted_score += sum(
                adjustment.score_delta
                for adjustment in attempt.league_entry.adjustments.all()
            )
        except LeagueScoreEntry.DoesNotExist:
            pass
        elapsed = max(
            0, int((attempt.submitted_at - attempt.started_at).total_seconds())
        )
        row = {
            "attempt_id": str(attempt.pk),
            "exam_id": str(attempt.exam_id),
            "exam_title": attempt.exam.title,
            "score": adjusted_score,
            "correct_count": attempt.correct_count,
            "wrong_count": attempt.wrong_count,
            "blank_count": attempt.blank_count,
            "submitted_at": attempt.submitted_at,
            "elapsed_seconds": elapsed,
        }
        key = (
            adjusted_score, attempt.correct_count, -attempt.wrong_count,
            -elapsed, str(attempt.pk)
        )
        previous = best_by_exam.get(attempt.exam_id)
        if previous is None or key > previous[0]:
            best_by_exam[attempt.exam_id] = (key, row)

    rows = [item[1] for item in best_by_exam.values()]
    rows.sort(key=lambda row: (
        -row["score"], -row["correct_count"], row["wrong_count"],
        row["elapsed_seconds"], row["attempt_id"]
    ))
    return rows[:limit]
