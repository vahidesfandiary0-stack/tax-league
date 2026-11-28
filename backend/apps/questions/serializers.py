from django.utils import timezone
from rest_framework import serializers

from .models import Question, QuestionOption, QuestionRevision


class PublicQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "position", "text"]


class PublicQuestionSerializer(serializers.ModelSerializer):
    options = PublicQuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "subject", "difficulty", "prompt", "options", "version"]


class DesignerQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "position", "text", "is_correct"]
        read_only_fields = ["id"]


class DesignerQuestionSerializer(serializers.ModelSerializer):
    options = DesignerQuestionOptionSerializer(many=True)
    review_status = serializers.CharField(source="status", read_only=True)
    review_feedback = serializers.CharField(source="review_reason", read_only=True)

    class Meta:
        model = Question
        fields = [
            "id", "subject", "difficulty", "prompt", "options", "explanation", "premium_analysis",
            "source_reference", "valid_from", "valid_until", "status",
            "review_status", "review_feedback", "version", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "review_status", "review_feedback", "version", "created_at", "updated_at"]

    def validate_options(self, value):
        if len(value) != 4:
            raise serializers.ValidationError("سؤال باید دقیقاً چهار گزینه داشته باشد.")
        if sum(1 for item in value if item.get("is_correct")) != 1:
            raise serializers.ValidationError("دقیقاً یک گزینه باید پاسخ صحیح باشد.")
        if len({item.get("position") for item in value}) != 4 or {item.get("position") for item in value} != {1, 2, 3, 4}:
            raise serializers.ValidationError("شماره گزینه‌ها باید از ۱ تا ۴ و بدون تکرار باشد.")
        if any(not str(item.get("text", "")).strip() for item in value):
            raise serializers.ValidationError("متن هر چهار گزینه الزامی است.")
        return value

    def validate(self, attrs):
        for field, label in (("prompt", "متن سؤال"), ("explanation", "پاسخ تشریحی"), ("source_reference", "استناد قانونی")):
            value = attrs.get(field, getattr(self.instance, field, "") if self.instance else "")
            if not str(value or "").strip():
                raise serializers.ValidationError({field: f"{label} الزامی است."})
        if attrs.get("difficulty", getattr(self.instance, "difficulty", None)) not in {
            Question.Difficulty.HARD, Question.Difficulty.VERY_HARD, Question.Difficulty.SPECIALIST
        }:
            raise serializers.ValidationError({"difficulty": "فقط سطح سخت، خیلی سخت یا تخصصی پذیرفته می‌شود."})
        valid_from = attrs.get("valid_from", getattr(self.instance, "valid_from", None))
        valid_until = attrs.get("valid_until", getattr(self.instance, "valid_until", None))
        if valid_from and valid_until and valid_until < valid_from:
            raise serializers.ValidationError({"valid_until": "پایان اعتبار نمی‌تواند قبل از شروع اعتبار باشد."})
        prompt = attrs.get("prompt", getattr(self.instance, "prompt", ""))
        duplicate = Question.objects.filter(prompt__iexact=prompt.strip()).exclude(pk=getattr(self.instance, "pk", None))
        if duplicate.exists():
            raise serializers.ValidationError({"prompt": "متنی بسیار مشابه در بانک سؤال وجود دارد؛ پیش از ارسال، یکتایی سؤال را بررسی کنید."})
        return attrs

    @staticmethod
    def _snapshot(question):
        return {
            "subject": question.subject,
            "difficulty": question.difficulty,
            "prompt": question.prompt,
            "explanation": question.explanation,
            "premium_analysis": question.premium_analysis,
            "source_reference": question.source_reference,
            "valid_from": question.valid_from.isoformat() if question.valid_from else None,
            "valid_until": question.valid_until.isoformat() if question.valid_until else None,
            "options": list(question.options.order_by("position").values("position", "text", "is_correct")),
        }

    def create(self, validated_data):
        options = validated_data.pop("options")
        question = Question.objects.create(
            author=self.context["request"].user,
            status=Question.Status.DRAFT,
            provenance=Question.Provenance.AUTHORED,
            **validated_data,
        )
        for option in options:
            QuestionOption.objects.create(question=question, **option)
        QuestionRevision.objects.create(
            question=question, version=question.version,
            snapshot=self._snapshot(question), changed_by=self.context["request"].user,
        )
        return question

    def update(self, instance, validated_data):
        if instance.author_id != self.context["request"].user.pk:
            raise serializers.ValidationError("فقط طراح سؤال می‌تواند پیش‌نویس خودش را ویرایش کند.")
        if instance.status not in (Question.Status.DRAFT, Question.Status.REJECTED):
            raise serializers.ValidationError("پس از ارسال برای داوری، ویرایش قفل است؛ ابتدا نتیجه داوری را دریافت کنید.")
        options = validated_data.pop("options", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if instance.status == Question.Status.REJECTED:
            instance.status = Question.Status.DRAFT
            instance.reviewer = None
            instance.review_decision = ""
            instance.review_reason = ""
            instance.reviewed_at = None
        instance.version += 1
        instance.save()
        if options is not None:
            instance.options.all().delete()
            for option in options:
                QuestionOption.objects.create(question=instance, **option)
        QuestionRevision.objects.create(
            question=instance, version=instance.version,
            snapshot=self._snapshot(instance), changed_by=self.context["request"].user,
        )
        return instance


class QuestionRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionRevision
        fields = ["version", "snapshot", "created_at", "changed_by"]
        read_only_fields = fields
