from django.urls import path

from .views import ActiveSeasonView, LeaderboardView, MyLeagueStatsView, ProvincialLeaderboardView, LeagueAppealListCreateView, LeagueAppealReviewView

urlpatterns = [
    path("season/", ActiveSeasonView.as_view(), name="league-active-season"),
    path("leaderboard/", LeaderboardView.as_view(), name="league-leaderboard"),
    path("provincial-leaderboard/", ProvincialLeaderboardView.as_view(), name="league-provincial-leaderboard"),
    path("me/", MyLeagueStatsView.as_view(), name="league-my-stats"),
    path("appeals/", LeagueAppealListCreateView.as_view(), name="league-appeals"),
    path("appeals/<uuid:appeal_id>/review/", LeagueAppealReviewView.as_view(), name="league-appeal-review"),
]
