from django.contrib import admin

from .models import Exam, ExamQuestion


class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "status", "duration_minutes", "counts_for_league", "created_at")
    list_filter = ("kind", "status", "counts_for_league")
    search_fields = ("title",)
    inlines = [ExamQuestionInline]
    readonly_fields = ("created_at",)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "question", "position", "points_correct", "points_wrong")
    list_filter = ("exam",)
