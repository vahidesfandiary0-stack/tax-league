from django.contrib import admin

from .models import TutorConversation, TutorMessage


class TutorMessageInline(admin.TabularInline):
    model = TutorMessage
    extra = 0
    can_delete = False
    readonly_fields = ("role", "content", "citations", "confidence", "created_at")
    fields = readonly_fields


@admin.register(TutorConversation)
class TutorConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at", "updated_at")
    search_fields = ("user__phone_number", "title")
    readonly_fields = ("user", "title", "created_at", "updated_at")
    inlines = [TutorMessageInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm("academy.view_tutorconversation")
