from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from config.admin_audit import record_admin_action
from .focus import get_exam_focus_state
from .models import Exam, ExamQuestion
from .services import publish_exam


def warn_admin_during_exam(request):
    if get_exam_focus_state()["active"]:
        messages.warning(
            request,
            "حالت تمرکز آزمون فعال است؛ دسترسی مدیریتی شما محفوظ است. برای حفظ عدالت، "
            "آزمون منتشرشده و سؤال منتشرشده طبق سیاست یکپارچگی قابل ویرایش مستقیم نیستند؛ "
            "اصلاحات را در نسخه یا آزمون جدید اعمال کنید.",
        )


@admin.action(description="انتشار مستقیم آزمون‌های آماده (فقط مالک)")
def publish_selected_exams(modeladmin, request, queryset):
    if not request.user.is_superuser:
        modeladmin.message_user(request, "انتشار نهایی فقط در اختیار مالک سامانه است.", level=messages.ERROR)
        return
    count = 0
    published = []
    for exam in queryset:
        try:
            publish_exam(exam.pk, request.user)
            published.append(exam)
            count += 1
        except (ValidationError, Exam.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{exam.title}: {exc}", level=messages.ERROR)
    record_admin_action(request.user, published, "انتشار آزمون توسط مالک")
    modeladmin.message_user(request, f"{count} آزمون منتشر شد.")


class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "status", "duration_minutes", "counts_for_league", "created_at")
    list_filter = ("kind", "status", "counts_for_league")
    search_fields = ("title",)
    inlines = [ExamQuestionInline]
    actions = [publish_selected_exams]
    readonly_fields = ("created_at", "status")

    def changelist_view(self, request, extra_context=None):
        warn_admin_during_exam(request)
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        warn_admin_during_exam(request)
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "question", "position", "points_correct", "points_wrong")
    list_filter = ("exam",)
