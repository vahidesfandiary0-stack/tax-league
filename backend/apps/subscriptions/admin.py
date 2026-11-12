from django.contrib import admin

from .models import SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "period", "duration_days", "price_irr", "is_active")
    list_filter = ("period", "is_active")
    search_fields = ("title",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "starts_at", "ends_at", "status")
    list_filter = ("status", "plan")
    search_fields = ("user__phone_number", "user__display_name")
    readonly_fields = ("user", "plan", "starts_at", "ends_at", "status", "source_order", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
