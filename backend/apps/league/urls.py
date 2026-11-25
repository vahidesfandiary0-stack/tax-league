from django.urls import path

from .views import ActiveSeasonView, LeaderboardView, ProvincialLeaderboardView, MyLeagueStatsView, LeagueAppealListCreateView, LeagueAppealReviewView
from .personal_views import LatestNightLeaderboardView, MyTopNightRecordsView, MyDetailedPerformanceView

urlpatterns = [
    path("season/", ActiveSeasonView.as_view(), name="league-active-season"),
    path("leaderboard/", LeaderboardView.as_view(), name="league-leaderboard"),
    path("provincial-leaderboard/", ProvincialLeaderboardView.as_view(), name="league-provincial-leaderboard"),
    path("latest-night/", LatestNightLeaderboardView.as_view(), name="league-latest-night"),
    path("me/top-records/", MyTopNightRecordsView.as_view(), name="league-my-top-night-records"),
    path("me/performance/", MyDetailedPerformanceView.as_view(), name="league-my-detailed-performance"),
    path("me/", MyLeagueStatsView.as_view(), name="league-my-stats"),
    path("appeals/", LeagueAppealListCreateView.as_view(), name="league-appeals"),
    path("appeals/<uuid:appeal_id>/review/", LeagueAppealReviewView.as_view(), name="league-appeal-review"),
]
