from rest_framework import serializers

from .models import SupportMessage, SupportTicket


class SupportMessageSerializer(serializers.ModelSerializer):
    sender_label = serializers.SerializerMethodField()

    class Meta:
        model = SupportMessage
        fields = ["id", "sender_label", "body", "is_staff_reply", "created_at"]
        read_only_fields = fields

    def get_sender_label(self, obj):
        if obj.is_staff_reply:
            return "پشتیبانی"
        return obj.sender.display_name or "کاربر"


class SupportTicketListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = ["id", "subject", "category", "status", "created_at", "updated_at", "last_message"]
        read_only_fields = fields

    def get_last_message(self, obj):
        message = obj.messages.order_by("-created_at", "-pk").first()
        return message.body[:160] if message else ""


class SupportTicketDetailSerializer(SupportTicketListSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)

    class Meta(SupportTicketListSerializer.Meta):
        fields = SupportTicketListSerializer.Meta.fields + ["messages"]


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    first_message = serializers.CharField(max_length=4000, write_only=True)

    class Meta:
        model = SupportTicket
        fields = ["id", "subject", "category", "first_message"]
        read_only_fields = ["id"]

    def validate_subject(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("عنوان درخواست نمی‌تواند خالی باشد.")
        return value

    def validate_first_message(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("متن درخواست نمی‌تواند خالی باشد.")
        return value


class SupportMessageCreateSerializer(serializers.Serializer):
    body = serializers.CharField(max_length=4000)

    def validate_body(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("متن پیام نمی‌تواند خالی باشد.")
        return value
