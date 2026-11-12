from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from config.admin_audit import record_admin_action
from .models import LeagueScoreEntry, LeagueSeason, LeagueSeasonEvent
from .services import activate_season, close_season


@admin.action(description="فعال‌سازی فصل‌های انتخاب‌شده")
def activate_selected_seasons(modeladmin, request, queryset):
    changed = []
    for season in queryset:
        try:
            changed.append(activate_season(season.pk, request.user))
        except (ValidationError, LeagueSeason.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{season.title}: {exc}", level=messages.ERROR)
    record_admin_action(request.user, changed, "فصل از طریق سرویس کنترل‌شده فعال شد.")
    if changed:
        modeladmin.message_user(request, f"{len(changed)} فصل فعال شد.", level=messages.SUCCESS)


@admin.action(description="بستن فصل‌های انتخاب‌شده (پس از زمان پایان)")
def close_selected_seasons(modeladmin, request, queryset):
    changed = []
    for season in queryset:
        try:
            changed.append(close_season(season.pk, request.user))
        except (ValidationError, LeagueSeason.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{season.title}: {exc}", level=messages.ERROR)
    record_admin_action(request.user, changed, "فصل از طریق سرویس کنترل‌شده بسته شد.")
    if changed:
        modeladmin.message_user(request, f"{len(changed)} فصل بسته شد.", level=messages.SUCCESS)


class LeagueSeasonEventInline(admin.TabularInline):
    model = LeagueSeasonEvent
    extra = 0
    can_delete = False
    fields = ("kind", "actor", "note", "created_at")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(LeagueSeason)
class LeagueSeasonAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "starts_at", "ends_at")
    list_filter = ("status",)
    search_fields = ("title",)
    readonly_fields = ("created_at", "status")
    inlines = [LeagueSeasonEventInline]
    actions = [activate_selected_seasons, close_selected_seasons]


@admin.register(LeagueSeasonEvent)
class LeagueSeasonEventAdmin(admin.ModelAdmin):
    list_display = ("season", "kind", "actor", "created_at")
    list_filter = ("kind",)
    search_fields = ("season__title", "actor__display_name")
    readonly_fields = ("season", "actor", "kind", "note", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
