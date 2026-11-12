from django.contrib import admin

from .models import SupportMessage, SupportTicket


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ("sender", "body", "is_staff_reply", "created_at")
    can_delete = False


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "category", "status", "created_at", "updated_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("subject", "user__phone_number", "user__display_name")
    readonly_fields = ("user", "subject", "category", "created_at", "updated_at")
    inlines = [SupportMessageInline]


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("ticket", "sender", "is_staff_reply", "created_at")
    list_filter = ("is_staff_reply", "created_at")
    search_fields = ("ticket__subject", "body")
    readonly_fields = ("ticket", "sender", "body", "is_staff_reply", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
