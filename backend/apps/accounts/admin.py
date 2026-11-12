from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import OTPChallenge, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("phone_number",)
    list_display = ("phone_number", "display_name", "is_staff", "is_active")
    search_fields = ("phone_number", "display_name")
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("اطلاعات", {"fields": ("display_name",)}),
        ("دسترسی", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("تاریخ‌ها", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("phone_number", "password1", "password2")}),
    )
    filter_horizontal = ("groups", "user_permissions")


@admin.register(OTPChallenge)
class OTPChallengeAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "created_at", "expires_at", "consumed_at", "attempts")
    readonly_fields = ("phone_number", "code_digest", "created_at", "expires_at", "consumed_at", "attempts", "request_ip")
    search_fields = ("phone_number",)
