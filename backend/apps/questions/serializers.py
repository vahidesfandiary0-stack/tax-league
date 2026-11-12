from rest_framework import serializers

from .models import Question, QuestionOption


class PublicQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "position", "text"]


class PublicQuestionSerializer(serializers.ModelSerializer):
    options = PublicQuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "subject", "difficulty", "prompt", "options", "version"]
