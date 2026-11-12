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


from .models import LeagueAppeal


class LeagueAppealCreateSerializer(serializers.Serializer):
    attempt_id = serializers.UUIDField()
    reason = serializers.CharField(max_length=200, trim_whitespace=True)
    details = serializers.CharField(max_length=4000, trim_whitespace=True)


class LeagueAppealReviewSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=[LeagueAppeal.Status.APPROVED, LeagueAppeal.Status.REJECTED])
    decision_note = serializers.CharField(max_length=1000, trim_whitespace=True)
    score_delta = serializers.IntegerField(required=False, allow_null=True)


class LeagueAppealSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.display_name", read_only=True, allow_null=True)

    class Meta:
        model = LeagueAppeal
        fields = ["id", "attempt_id", "reason", "details", "status", "decision_note", "score_delta", "reviewer_name", "reviewed_at", "created_at"]
        read_only_fields = fields
