from django.contrib import admin

from .models import AcademyContent


@admin.register(AcademyContent)
class AcademyContentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_exclusive", "is_active", "sort_order", "updated_at")
    list_editable = ("is_exclusive", "is_active", "sort_order")
    list_filter = ("category", "is_exclusive", "is_active")
    search_fields = ("title", "summary", "body", "source_title")
    ordering = ("sort_order", "-updated_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("محتوا", {"fields": ("slug", "title", "summary", "category", "body")}),
        ("منبع و اعتبار", {"fields": ("source_title", "source_url", "legal_effective_date")}),
        ("دسترسی و انتشار", {"fields": ("is_exclusive", "is_active", "sort_order")}),
        ("سوابق", {"fields": ("created_at", "updated_at")}),
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
