from django.urls import path

from .views import ActiveSeasonView, LeaderboardView, MyLeagueStatsView

urlpatterns = [
    path("season/", ActiveSeasonView.as_view(), name="league-active-season"),
    path("leaderboard/", LeaderboardView.as_view(), name="league-leaderboard"),
    path("me/", MyLeagueStatsView.as_view(), name="league-my-stats"),
]
