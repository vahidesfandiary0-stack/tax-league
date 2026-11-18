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
    class Meta:
        model = ExamAttempt
        fields = ["id", "status", "score", "correct_count", "wrong_count", "blank_count", "submitted_at"]


class ResultListSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="exam.title", read_only=True)

    class Meta:
        model = ExamAttempt
        fields = [
            "id", "exam", "exam_title", "status", "score",
            "correct_count", "wrong_count", "blank_count", "submitted_at",
        ]



class PremiumLessonSerializer(serializers.Serializer):
    traps_and_techniques = serializers.CharField()
    trap_detection_signals = serializers.CharField()
    distractor_analysis = serializers.CharField()
    fast_solving_method = serializers.CharField()
    common_mistakes = serializers.CharField()
    supplementary_practice = serializers.CharField()
    practice_answer = serializers.CharField()
    legal_source_reference = serializers.CharField()
    legal_effective_date = serializers.DateField(allow_null=True)


class AttemptReviewQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    selected_option_id = serializers.SerializerMethodField()
    premium_locked = serializers.SerializerMethodField()
    premium_lesson = serializers.SerializerMethodField()

    class Meta:
        model = AttemptQuestion
        fields = [
            "id", "position", "prompt", "subject", "explanation",
            "options", "selected_option_id", "premium_locked", "premium_lesson",
        ]

    def get_options(self, obj):
        return [
            {
                "id": option.pk,
                "position": option.position,
                "text": option.text,
                "is_correct": option.is_correct,
            }
            for option in obj.options.all()
        ]

    def get_selected_option_id(self, obj):
        answer = getattr(obj, "answer", None)
        return answer.selected_option_id if answer else None

    def _lesson(self, obj):
        if not self.context.get("has_premium_access"):
            return None
        from apps.questions.models import QuestionPremiumLesson
        return QuestionPremiumLesson.objects.filter(
            question_id=obj.source_question_id,
            status=QuestionPremiumLesson.Status.PUBLISHED,
        ).first()

    def get_premium_locked(self, obj):
        if not self.context.get("has_premium_access"):
            from apps.questions.models import QuestionPremiumLesson
            return QuestionPremiumLesson.objects.filter(
                question_id=obj.source_question_id,
                status=QuestionPremiumLesson.Status.PUBLISHED,
            ).exists()
        return False

    def get_premium_lesson(self, obj):
        lesson = self._lesson(obj)
        return PremiumLessonSerializer(lesson).data if lesson else None


class AttemptReviewSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = ExamAttempt
        fields = [
            "id", "exam", "status", "score", "correct_count",
            "wrong_count", "blank_count", "submitted_at", "questions",
        ]

    def get_questions(self, obj):
        from .models import AttemptQuestion
        questions = obj.questions.prefetch_related("options", "answer__selected_option").all()
        return AttemptReviewQuestionSerializer(
            questions, many=True, context=self.context
        ).data
