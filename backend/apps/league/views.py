from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LeagueSeason
from .serializers import LeagueSeasonSerializer
from .services import leaderboard_for_season, league_rows_for_season


def requested_season(request):
    season_id = request.query_params.get("season")
    if season_id:
        try:
            return LeagueSeason.objects.filter(
                pk=season_id,
                status__in=[LeagueSeason.Status.ACTIVE, LeagueSeason.Status.CLOSED],
            ).first()
        except (ValueError, TypeError):
            return None
    active = LeagueSeason.objects.filter(
        status=LeagueSeason.Status.ACTIVE
    ).order_by("-starts_at").first()
    if active:
        return active
    return LeagueSeason.objects.filter(
        status=LeagueSeason.Status.CLOSED
    ).order_by("-ends_at").first()


class ActiveSeasonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        season = LeagueSeason.objects.filter(
            status=LeagueSeason.Status.ACTIVE
        ).order_by("-starts_at").first()
        if not season:
            return Response({"season": None, "detail": "در حال حاضر فصل فعالی وجود ندارد."})
        return Response({"season": LeagueSeasonSerializer(season).data})


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        season = requested_season(request)
        if not season:
            return Response({"season": None, "results": []})
        try:
            limit = int(request.query_params.get("limit", 100))
        except (TypeError, ValueError):
            return Response({"detail": "پارامتر limit باید عدد صحیح باشد."}, status=400)
        if not 1 <= limit <= 500:
            return Response({"detail": "limit باید بین ۱ تا ۵۰۰ باشد."}, status=400)

        _, rows = leaderboard_for_season(season.pk, limit=limit)
        results = []
        for index, row in enumerate(rows, start=1):
            results.append({
                "rank": index,
                "display_name": row["user__display_name"] or "کاربر",
                "total_score": row["total_score"],
                "correct_total": row["correct_total"],
                "wrong_total": row["wrong_total"],
                "exams_count": row["exams_count"],
            })
        return Response({"season": LeagueSeasonSerializer(season).data, "results": results})


class ProvincialLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        province = (getattr(request.user, "province", "") or "").strip()
        verified = bool(getattr(request.user, "province_verified", False) and province)
        if not verified:
            return Response({
                "season": None,
                "province": province,
                "verified": False,
                "results": [],
            })

        season = requested_season(request)
        if not season:
            return Response({
                "season": None,
                "province": province,
                "verified": True,
                "results": [],
            })
        try:
            limit = int(request.query_params.get("limit", 100))
        except (TypeError, ValueError):
            return Response({"detail": "پارامتر limit باید عدد صحیح باشد."}, status=400)
        if not 1 <= limit <= 500:
            return Response({"detail": "limit باید بین ۱ تا ۵۰۰ باشد."}, status=400)

        _, rows = leaderboard_for_season(season.pk, limit=limit, province=province)
        results = [
            {
                "rank": index,
                "display_name": row["user__display_name"] or "کاربر",
                "total_score": row["total_score"],
                "correct_total": row["correct_total"],
                "wrong_total": row["wrong_total"],
                "exams_count": row["exams_count"],
            }
            for index, row in enumerate(rows, start=1)
        ]
        return Response({
            "season": LeagueSeasonSerializer(season).data,
            "province": province,
            "verified": True,
            "results": results,
        })


class MyLeagueStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        season = requested_season(request)
        if not season:
            return Response({
                "season": None, "rank": None, "total_score": 0, "exams_count": 0
            })
        _, rows = league_rows_for_season(season.pk)
        rank = None
        total_score = 0
        exams_count = 0
        for index, row in enumerate(rows, start=1):
            if row["user_id"] == request.user.pk:
                rank = index
                total_score = row["total_score"]
                exams_count = row["exams_count"]
                break
        return Response({
            "season": LeagueSeasonSerializer(season).data,
            "rank": rank,
            "total_score": total_score,
            "exams_count": exams_count,
        })


from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from rest_framework import status
from .models import LeagueAppeal
from .serializers import LeagueAppealCreateSerializer, LeagueAppealReviewSerializer, LeagueAppealSerializer
from .services import file_league_appeal, review_league_appeal


class LeagueAppealListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = LeagueAppeal.objects.select_related("attempt", "reviewer", "user")
        if not (request.user.is_superuser or (request.user.is_staff and request.user.has_perm("league.view_leagueappeal"))):
            qs = qs.filter(user=request.user)
        return Response(LeagueAppealSerializer(qs[:100], many=True).data)

    def post(self, request):
        serializer = LeagueAppealCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            appeal = file_league_appeal(**serializer.validated_data, user=request.user)
        except (DjangoValidationError, ObjectDoesNotExist, ValueError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LeagueAppealSerializer(appeal).data, status=status.HTTP_201_CREATED)


class LeagueAppealReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appeal_id):
        serializer = LeagueAppealReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            appeal = review_league_appeal(appeal_id, request.user, data["decision"], data["decision_note"], data.get("score_delta"))
        except (DjangoValidationError, LeagueAppeal.DoesNotExist, ValueError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(LeagueAppealSerializer(appeal).data)


class LatestNightExamLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .services import latest_night_exam_rows

        exam, national_rows = latest_night_exam_rows()
        if exam is None:
            return Response({
                "exam": None,
                "national_results": [],
                "province": None,
                "province_verified": bool(
                    getattr(request.user, "province_verified", False)
                    and getattr(request.user, "province", "")
                ),
                "provincial_results": [],
            })

        def serialize(rows):
            return [
                {
                    "rank": index,
                    "display_name": row.user.display_name or "کاربر",
                    "total_score": row.adjusted_score,
                    "correct_total": row.correct_count,
                    "wrong_total": row.wrong_count,
                    "elapsed_seconds": row.elapsed_seconds,
                    "attempt_id": str(row.attempt_id),
                }
                for index, row in enumerate(rows, start=1)
            ]

        province = (getattr(request.user, "province", "") or "").strip()
        verified = bool(
            getattr(request.user, "province_verified", False) and province
        )

        provincial_rows = []
        if verified:
            provincial_exam, provincial_rows = latest_night_exam_rows(
                province=province
            )
            # Both calls must refer to the same latest exam.
            if provincial_exam is None or provincial_exam.pk != exam.pk:
                provincial_rows = []

        return Response({
            "exam": {
                "id": str(exam.pk),
                "title": exam.title,
                "starts_at": exam.starts_at,
                "ends_at": exam.ends_at,
            },
            "national_results": serialize(national_rows),
            "province": province if verified else None,
            "province_verified": verified,
            "provincial_results": serialize(provincial_rows),
        })


class MyTopRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .services import top_records_for_user

        records = top_records_for_user(request.user, limit=5)
        return Response({
            "results": [
                {
                    "attempt_id": str(entry.attempt_id),
                    "exam_id": str(entry.attempt.exam_id),
                    "exam_title": entry.attempt.exam.title,
                    "season_id": str(entry.season_id),
                    "season_title": entry.season.title,
                    "score": entry.score,
                    "adjusted_score": entry.adjusted_score,
                    "correct_count": entry.correct_count,
                    "wrong_count": entry.wrong_count,
                    "elapsed_seconds": entry.elapsed_seconds,
                    "submitted_at": entry.attempt.submitted_at,
                }
                for entry in records
            ]
        })


class MyPerformanceAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Avg, Count, Sum
        from django.utils import timezone
        from apps.exams.models import ExamAttempt
        from apps.subscriptions.models import UserSubscription

        now = timezone.now()
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status=UserSubscription.Status.ACTIVE,
            starts_at__lte=now,
            ends_at__gt=now,
        ).select_related("plan").order_by("-ends_at").first()

        if subscription is None:
            return Response(
                {
                    "active": False,
                    "subscription_required": True,
                    "detail": "برای مشاهده تحلیل تفصیلی، اشتراک فعال لازم است.",
                },
                status=403,
            )

        attempts = ExamAttempt.objects.filter(
            user=request.user,
            status__in=[
                ExamAttempt.Status.SUBMITTED,
                ExamAttempt.Status.EXPIRED,
            ],
            submitted_at__isnull=False,
            score__isnull=False,
        )

        summary = attempts.aggregate(
            attempt_count=Count("id"),
            average_score=Avg("score"),
            total_correct=Sum("correct_count"),
            total_wrong=Sum("wrong_count"),
            total_blank=Sum("blank_count"),
        )

        by_kind = list(
            attempts.values("exam__kind").annotate(
                attempt_count=Count("id"),
                average_score=Avg("score"),
                total_correct=Sum("correct_count"),
                total_wrong=Sum("wrong_count"),
                total_blank=Sum("blank_count"),
            ).order_by("exam__kind")
        )

        average = summary["average_score"]
        summary["average_score"] = round(float(average), 2) if average is not None else None

        for item in by_kind:
            value = item["average_score"]
            item["average_score"] = round(float(value), 2) if value is not None else None

        return Response({
            "active": True,
            "subscription": {
                "plan": subscription.plan.title,
                "ends_at": subscription.ends_at,
            },
            "summary": {
                "attempt_count": summary["attempt_count"] or 0,
                "average_score": summary["average_score"],
                "total_correct": summary["total_correct"] or 0,
                "total_wrong": summary["total_wrong"] or 0,
                "total_blank": summary["total_blank"] or 0,
            },
            "by_exam_kind": by_kind,
        })
