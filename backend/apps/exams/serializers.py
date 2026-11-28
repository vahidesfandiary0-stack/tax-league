from django.utils import timezone
from apps.subscriptions.models import UserSubscription
from rest_framework import serializers

from .models import AttemptAnswer, AttemptQuestion, Exam, ExamAttempt


class ExamListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source="exam_questions.count", read_only=True)
    server_now = serializers.SerializerMethodField()

    def get_server_now(self, obj):
        return timezone.now().isoformat()

    class Meta:
        model = Exam
        fields = ["id", "title", "kind", "description", "duration_minutes", "starts_at", "ends_at", "question_count", "counts_for_league", "server_now"]


class AttemptOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    position = serializers.IntegerField()
    text = serializers.CharField()


class AttemptQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    selected_option_id = serializers.SerializerMethodField()

    class Meta:
        model = AttemptQuestion
        fields = ["id", "position", "prompt", "subject", "options", "selected_option_id"]

    def get_options(self, obj):
        return AttemptOptionSerializer(obj.options.all(), many=True).data

    def get_selected_option_id(self, obj):
        answer = getattr(obj, "answer", None)
        return answer.selected_option_id if answer else None


class AttemptSerializer(serializers.ModelSerializer):
    questions = AttemptQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = ExamAttempt
        fields = ["id", "exam", "status", "started_at", "deadline_at", "questions"]


class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField()


class ResultSerializer(serializers.ModelSerializer):
    question_reviews = serializers.SerializerMethodField()

    class Meta:
        model = ExamAttempt
        fields = ["id", "status", "score", "correct_count", "wrong_count", "blank_count", "submitted_at", "question_reviews"]

    def get_question_reviews(self, obj):
        if obj.status not in (ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.EXPIRED):
            return []
        now = timezone.now()
        is_subscriber = UserSubscription.objects.filter(
            user=obj.user, status=UserSubscription.Status.ACTIVE,
            starts_at__lte=now, ends_at__gt=now,
        ).exists()
        reviews = []
        for question in obj.questions.prefetch_related("options", "answer__selected_option"):
            answer = getattr(question, "answer", None)
            selected = answer.selected_option if answer else None
            options = []
            for option in question.options.all():
                row = {
                    "id": option.pk, "position": option.position, "text": option.text,
                    "is_correct": option.is_correct,
                    "selected": bool(selected and selected.pk == option.pk),
                }
                if is_subscriber:
                    premium = question.premium_analysis or {}
                    for note in premium.get("option_analyses", []):
                        if note.get("option_text") == option.text:
                            row["premium_analysis"] = note.get("analysis", "")
                            break
                options.append(row)
            item = {
                "id": question.pk, "position": question.position, "prompt": question.prompt,
                "explanation": question.explanation, "source_reference": question.source_reference,
                "options": options,
            }
            if is_subscriber:
                item["premium_analysis"] = question.premium_analysis
            reviews.append(item)
        return reviews


class ResultListSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    counts_for_league = serializers.BooleanField(source="exam.counts_for_league", read_only=True)

    class Meta:
        model = ExamAttempt
        fields = [
            "id", "exam", "exam_title", "counts_for_league", "status", "score",
            "correct_count", "wrong_count", "blank_count", "submitted_at",
        ]
