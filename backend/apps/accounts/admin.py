from django.contrib import admin

from .models import OTPChallenge, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "display_name", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("phone_number", "display_name")
    readonly_fields = ("password", "last_login", "date_joined")
    fields = (
        "phone_number", "display_name", "is_active", "is_staff",
        "is_superuser", "groups", "user_permissions",
        "password", "last_login", "date_joined",
    )

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(OTPChallenge)
class OTPChallengeAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "created_at", "expires_at", "consumed_at", "attempts")
    readonly_fields = (
        "phone_number", "code_digest", "created_at", "expires_at",
        "consumed_at", "attempts", "request_ip",
    )
    search_fields = ("phone_number",)
    def has_add_permission(self, request):
        return False
