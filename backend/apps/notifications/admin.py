from django.contrib import admin

from .models import Notification, ShowcaseSlide


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "kind", "title", "created_at", "read_at")
    list_filter = ("kind", "created_at")
    search_fields = ("recipient__phone_number", "title", "body")
    readonly_fields = ("created_at", "read_at")
    ordering = ("-created_at",)

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


@admin.register(ShowcaseSlide)
class ShowcaseSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "is_active", "sort_order", "duration_seconds", "starts_at", "ends_at", "updated_at")
    list_editable = ("is_active", "sort_order", "duration_seconds")
    list_filter = ("kind", "is_active")
    search_fields = ("title", "body")
    ordering = ("sort_order", "pk")
    readonly_fields = ("created_at", "updated_at")
    save_on_top = True
    fieldsets = (
        ("محتوا", {"fields": ("kind", "title", "body", "image", "image_url")}),
        ("نمایش", {"fields": ("is_active", "sort_order", "duration_seconds", "starts_at", "ends_at")}),
        ("سوابق", {"fields": ("created_at", "updated_at")}),
    )

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff
