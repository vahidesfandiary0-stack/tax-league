from datetime import timedelta

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from .focus import get_exam_focus_state
from .models import Exam, ExamQuestion
from .services import publish_exam


def warn_admin_during_exam(request):
    if get_exam_focus_state()["active"]:
        messages.warning(
            request,
            "حالت تمرکز آزمون فعال است؛ دسترسی مدیریتی شما محفوظ است. "
            "تغییرات مدیریتی آزمون و سؤال ثبت می‌شود و نسخهٔ سؤال‌های تلاش‌های قبلی ثابت می‌ماند.",
        )


@admin.action(description="انتشار آزمون‌های پیش‌نویسِ معتبر")
def publish_selected_exams(modeladmin, request, queryset):
    count = 0
    for exam in queryset:
        try:
            publish_exam(exam.pk)
            count += 1
        except (ValidationError, Exam.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{exam.title}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{count} آزمون منتشر شد.")


@admin.action(description="انتشار و شروع فوری آزمون‌های انتخاب‌شده")
def publish_and_start_now_selected_exams(modeladmin, request, queryset):
    count = 0
    for exam in queryset:
        try:
            if exam.status != Exam.Status.DRAFT:
                raise ValidationError("فقط آزمون پیش‌نویس قابل شروع فوری است.")
            launch_time = timezone.now()
            exam.starts_at = launch_time
            exam.ends_at = launch_time + timedelta(minutes=exam.duration_minutes)
            exam.save(update_fields=["starts_at", "ends_at"])
            publish_exam(exam.pk)
            count += 1
        except (ValidationError, Exam.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{exam.title}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{count} آزمون فوراً منتشر و فعال شد.")


@admin.action(description="توقف/لغو آزمون‌های انتخاب‌شده")
def archive_selected_exams(modeladmin, request, queryset):
    count = queryset.exclude(status=Exam.Status.ARCHIVED).update(status=Exam.Status.ARCHIVED)
    modeladmin.message_user(request, f"{count} آزمون متوقف و بایگانی شد.")


class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "status", "duration_minutes", "counts_for_league", "created_at")
    list_filter = ("kind", "status", "counts_for_league")
    search_fields = ("title",)
    inlines = [ExamQuestionInline]
    actions = [publish_selected_exams, publish_and_start_now_selected_exams, archive_selected_exams]
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
