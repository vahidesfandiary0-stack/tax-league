from rest_framework import serializers

from .models import AcademyContent


class AcademyContentListSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    source_title = serializers.SerializerMethodField()

    class Meta:
        model = AcademyContent
        fields = [
            "id", "slug", "title", "summary", "category", "is_exclusive",
            "is_locked", "source_title", "legal_effective_date",
        ]

    def get_is_locked(self, obj):
        return bool(obj.is_exclusive and not self.context.get("has_subscription", False))

    def get_source_title(self, obj):
        if obj.is_exclusive and not self.context.get("has_subscription", False):
            return None
        return obj.source_title


class AcademyContentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademyContent
        fields = [
            "id", "slug", "title", "summary", "category", "body",
            "source_title", "source_url", "legal_effective_date", "updated_at",
        ]
