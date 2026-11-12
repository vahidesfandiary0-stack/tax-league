from django.db.models import Sum, Count, IntegerField, Value
from django.db.models.functions import Coalesce
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LeagueSeason, LeagueScoreEntry
from .serializers import LeagueSeasonSerializer
from .services import leaderboard_for_season


class ActiveSeasonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        season = LeagueSeason.objects.filter(status=LeagueSeason.Status.ACTIVE).order_by("-starts_at").first()
        if not season:
            return Response({"season": None, "detail": "در حال حاضر فصل فعالی وجود ندارد."})
        return Response({"season": LeagueSeasonSerializer(season).data})


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        season_id = request.query_params.get("season")
        if season_id:
            try:
                season, rows = leaderboard_for_season(season_id)
            except LeagueSeason.DoesNotExist:
                return Response({"detail": "فصل پیدا نشد."}, status=404)
        else:
            season = LeagueSeason.objects.filter(status=LeagueSeason.Status.ACTIVE).order_by("-starts_at").first()
            if not season:
                return Response({"season": None, "results": []})
            _, rows = leaderboard_for_season(season.pk)

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
        season = LeagueSeason.objects.filter(status=LeagueSeason.Status.ACTIVE).order_by("-starts_at").first()
        if not season:
            return Response({"season": None, "rank": None, "total_score": 0, "exams_count": 0})
        totals = LeagueScoreEntry.objects.filter(season=season, user=request.user).aggregate(
            total_score=Coalesce(Sum("score"), Value(0), output_field=IntegerField()),
            exams_count=Count("id"),
        )
        all_rows = list(LeagueScoreEntry.objects.filter(season=season).values("user_id").annotate(
            total_score=Coalesce(Sum("score"), Value(0), output_field=IntegerField()),
            correct_total=Coalesce(Sum("correct_count"), Value(0), output_field=IntegerField()),
            wrong_total=Coalesce(Sum("wrong_count"), Value(0), output_field=IntegerField()),
            total_time=Coalesce(Sum("elapsed_seconds"), Value(0), output_field=IntegerField()),
        ).order_by("-total_score", "-correct_total", "wrong_total", "total_time", "user_id"))
        rank = next((i for i, row in enumerate(all_rows, 1) if row["user_id"] == request.user.pk), None)
        return Response({
            "season": LeagueSeasonSerializer(season).data,
            "rank": rank,
            "total_score": totals["total_score"],
            "exams_count": totals["exams_count"],
        })
