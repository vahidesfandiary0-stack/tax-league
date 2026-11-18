from rest_framework import serializers

from .models import TutorConversation, TutorMessage


class TutorMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorMessage
        fields = ["id", "role", "content", "citations", "confidence", "created_at"]


class TutorConversationSerializer(serializers.ModelSerializer):
    messages = TutorMessageSerializer(many=True, read_only=True)

    class Meta:
        model = TutorConversation
        fields = ["id", "title", "created_at", "updated_at", "messages"]
