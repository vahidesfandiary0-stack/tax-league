from django.contrib import admin

from .models import LeagueScoreEntry, LeagueSeason


@admin.register(LeagueSeason)
class LeagueSeasonAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "starts_at", "ends_at")
    list_filter = ("status",)
    search_fields = ("title",)
    readonly_fields = ("created_at",)


@admin.register(LeagueScoreEntry)
class LeagueScoreEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "season", "score", "correct_count", "wrong_count", "recorded_at")
    list_filter = ("season",)
    search_fields = ("user__display_name", "user__phone_number")
    readonly_fields = (
        "season", "attempt", "user", "score", "correct_count",
        "wrong_count", "elapsed_seconds", "recorded_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
