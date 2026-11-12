from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import PaymentOrder, PaymentSettings
from .services import approve_order, reject_order


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "updated_at")
    fields = ("card_number", "account_holder", "updated_at")
    readonly_fields = ("updated_at",)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser and not PaymentSettings.objects.exists()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product_type", "amount_irr", "status", "created_at")
    list_filter = ("status", "product_type")
    search_fields = ("id", "user__phone_number", "tracking_code")
    readonly_fields = (
        "user", "product_type", "plan", "exam", "amount_irr",
        "tracking_code", "user_note", "reviewer", "review_note", "reviewed_at",
        "created_at", "updated_at",
    )
    actions = ("approve_selected", "reject_selected")

    def has_add_permission(self, request):
        return False

    @admin.action(description="تأیید سفارش‌های انتخاب‌شده")
    def approve_selected(self, request, queryset):
        for order in queryset:
            try:
                approve_order(order.pk, request.user)
            except ValidationError as exc:
                self.message_user(request, f"{order.pk}: {exc}", level=messages.ERROR)

    @admin.action(description="رد سفارش‌های انتخاب‌شده")
    def reject_selected(self, request, queryset):
        for order in queryset:
            try:
                reject_order(order.pk, request.user, "ردشده توسط مدیر")
            except ValidationError as exc:
                self.message_user(request, f"{order.pk}: {exc}", level=messages.ERROR)

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False
