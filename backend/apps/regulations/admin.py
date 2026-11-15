from django.contrib import admin
from .models import (
    RegulationSource,
    RegulationDocument,
    RegulationVersion,
    RegulationChange,
)


@admin.register(RegulationSource)
class RegulationSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "base_url", "is_active", "check_interval_hours", "last_success_at")
    list_filter = ("is_active",)
    search_fields = ("name", "base_url")
    readonly_fields = ("last_checked_at", "last_success_at", "last_error", "created_at")


@admin.register(RegulationDocument)
class RegulationDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title", "document_type", "official_number",
        "issuing_authority", "legal_status", "publication_date",
    )
    list_filter = ("document_type", "legal_status", "issuing_authority")
    search_fields = ("title", "official_number", "issuing_authority")
    readonly_fields = ("first_seen_at", "last_seen_at", "created_at", "updated_at")
    date_hierarchy = "publication_date"


@admin.register(RegulationVersion)
class RegulationVersionAdmin(admin.ModelAdmin):
    list_display = (
        "document", "version_number", "extraction_method",
        "extraction_quality", "is_reviewed", "captured_at",
    )
    list_filter = ("is_reviewed", "extraction_method")
    search_fields = ("document__title", "content", "content_sha256")
    readonly_fields = ("captured_at", "content_sha256")


@admin.register(RegulationChange)
class RegulationChangeAdmin(admin.ModelAdmin):
    list_display = (
        "document", "change_type", "review_status",
        "detected_at", "reviewed_by",
    )
    list_filter = ("change_type", "review_status")
    search_fields = ("document__title", "summary", "review_note")
    readonly_fields = ("detected_at",)
