from rest_framework import serializers

from .models import AttemptAnswer, AttemptQuestion, Exam, ExamAttempt


class ExamListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source="exam_questions.count", read_only=True)

    class Meta:
        model = Exam
        fields = ["id", "title", "kind", "description", "duration_minutes", "starts_at", "ends_at", "question_count"]


class AttemptOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    position = serializers.IntegerField()
    text = serializers.CharField()


class AttemptQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = AttemptQuestion
        fields = ["id", "position", "prompt", "subject", "options"]

    def get_options(self, obj):
        return AttemptOptionSerializer(obj.options.all(), many=True).data


class AttemptSerializer(serializers.ModelSerializer):
    questions = AttemptQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = ExamAttempt
        fields = ["id", "exam", "status", "started_at", "deadline_at", "questions"]


class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField()


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ["id", "status", "score", "correct_count", "wrong_count", "blank_count", "submitted_at"]
