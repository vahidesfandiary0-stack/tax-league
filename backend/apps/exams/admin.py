from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Exam, ExamQuestion
from .services import publish_exam


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
    readonly_fields = ("created_at",)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "question", "position", "points_correct", "points_wrong")
    list_filter = ("exam",)
