from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from config.admin_audit import record_admin_action

from .models import Question, QuestionOption
from .services import publish_question, review_question, submit_for_review


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4
    max_num = 4


@admin.action(description="ارسال سؤالات انتخاب‌شده برای بررسی (توسط نویسنده)")
def submit_selected(modeladmin, request, queryset):
    count = 0
    changed = []
    for question in queryset:
        try:
            submit_for_review(question.pk, request.user)
            changed.append(question)
            count += 1
        except (ValidationError, Question.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{question.pk}: {exc}", level=messages.ERROR)
    record_admin_action(request.user, changed, "ارسال سؤال برای بازبینی")
    modeladmin.message_user(request, f"{count} سؤال ارسال شد.")


@admin.action(description="تأیید سؤالات انتخاب‌شده (بازبین غیرنویسنده)")
def approve_selected(modeladmin, request, queryset):
    count = 0
    changed = []
    for question in queryset:
        try:
            review_question(question.pk, request.user, True, "تأیید از پنل مدیریت")
            changed.append(question)
            count += 1
        except (ValidationError, Question.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{question.pk}: {exc}", level=messages.ERROR)
    record_admin_action(request.user, changed, "تأیید سؤال توسط بازبین")
    modeladmin.message_user(request, f"{count} سؤال تأیید شد.")


@admin.action(description="رد سؤالات انتخاب‌شده")
def reject_selected(modeladmin, request, queryset):
    count = 0
    changed = []
    for question in queryset:
        try:
            review_question(question.pk, request.user, False, "رد از پنل مدیریت")
            changed.append(question)
            count += 1
        except (ValidationError, Question.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{question.pk}: {exc}", level=messages.ERROR)
    record_admin_action(request.user, changed, "رد سؤال توسط بازبین")
    modeladmin.message_user(request, f"{count} سؤال رد شد.")


@admin.action(description="انتشار سؤالات تأییدشده")
def publish_selected(modeladmin, request, queryset):
    count = 0
    for question in queryset:
        try:
            publish_question(question.pk)
            count += 1
        except (ValidationError, Question.DoesNotExist) as exc:
            modeladmin.message_user(request, f"{question.pk}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{count} سؤال منتشر شد.")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "difficulty", "provenance", "status", "author", "reviewer", "version", "created_at")
    list_filter = ("subject", "difficulty", "provenance", "status")
    search_fields = ("prompt", "source_reference", "author__phone_number")
    readonly_fields = ("reviewer", "review_decision", "review_reason", "reviewed_at", "published_at", "created_at", "updated_at")
    inlines = [QuestionOptionInline]
    actions = [submit_selected, approve_selected, reject_selected, publish_selected]
