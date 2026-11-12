from rest_framework import serializers

from .models import LeagueSeason


class LeagueSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeagueSeason
        fields = ["id", "title", "starts_at", "ends_at", "status"]


class LeaderboardRowSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    display_name = serializers.CharField()
    total_score = serializers.IntegerField()
    correct_total = serializers.IntegerField()
    wrong_total = serializers.IntegerField()
    exams_count = serializers.IntegerField()
