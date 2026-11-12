from django.db.models import Count, F, IntegerField, Sum, Value, Window, OuterRef, Subquery
from django.db.models.functions import Coalesce, RowNumber
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LeagueSeason, LeagueScoreEntry, LeagueScoreAdjustment
from .serializers import LeagueSeasonSerializer
from .services import leaderboard_for_season


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


class MyLeagueStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        season = requested_season(request)
        if not season:
            return Response({
                "season": None, "rank": None, "total_score": 0, "exams_count": 0
            })
        base_totals = LeagueScoreEntry.objects.filter(
            season=season, user=request.user
        ).aggregate(
            base_score=Coalesce(Sum("score"), Value(0), output_field=IntegerField()),
            exams_count=Count("id"),
        )
        correction = LeagueScoreAdjustment.objects.filter(
            entry__season=season, entry__user=request.user
        ).aggregate(total=Coalesce(Sum("score_delta"), Value(0), output_field=IntegerField()))["total"]
        total_score = base_totals["base_score"] + correction
        ranked_user = (
            LeagueScoreEntry.objects.filter(season=season)
            .values("season_id", "user_id")
            .annotate(
                base_score=Coalesce(Sum("score"), Value(0), output_field=IntegerField()),
                correct_total=Coalesce(Sum("correct_count"), Value(0), output_field=IntegerField()),
                wrong_total=Coalesce(Sum("wrong_count"), Value(0), output_field=IntegerField()),
                total_time=Coalesce(Sum("elapsed_seconds"), Value(0), output_field=IntegerField()),
            )
            .annotate(
                adjustment_total=Coalesce(
                    Subquery(
                        LeagueScoreAdjustment.objects.filter(
                            entry__season_id=OuterRef("season_id"),
                            entry__user_id=OuterRef("user_id"),
                        ).values("entry__user_id").annotate(total=Sum("score_delta")).values("total")[:1],
                        output_field=IntegerField(),
                    ), Value(0), output_field=IntegerField(),
                )
            )
            .annotate(total_score=F("base_score") + F("adjustment_total"))
            .annotate(
                rank=Window(
                    expression=RowNumber(),
                    order_by=[
                        F("total_score").desc(),
                        F("correct_total").desc(),
                        F("wrong_total").asc(),
                        F("total_time").asc(),
                        F("user_id").asc(),
                    ],
                )
            )
            .filter(user_id=request.user.pk)
            .values_list("rank", flat=True)
            .first()
        )
        rank = int(ranked_user) if ranked_user is not None else None
        return Response({
            "season": LeagueSeasonSerializer(season).data,
            "rank": rank,
            "total_score": total_score,
            "exams_count": base_totals["exams_count"],
        })


from django.core.exceptions import ValidationError as DjangoValidationError
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
        except (DjangoValidationError, LeagueAppeal.DoesNotExist, ValueError) as exc:
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
