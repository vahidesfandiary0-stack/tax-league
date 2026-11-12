from rest_framework import serializers

from .models import PaymentOrder
from apps.subscriptions.models import SubscriptionPlan


class CreateOrderSerializer(serializers.Serializer):
    product_type = serializers.ChoiceField(choices=PaymentOrder.ProductType.choices)
    plan_id = serializers.UUIDField(required=False)
    exam_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        if attrs["product_type"] == PaymentOrder.ProductType.SUBSCRIPTION:
            if not attrs.get("plan_id") or attrs.get("exam_id"):
                raise serializers.ValidationError("برای سفارش اشتراک فقط plan_id را ارسال کنید.")
        elif not attrs.get("exam_id") or attrs.get("plan_id"):
            raise serializers.ValidationError("برای سفارش آزمون فقط exam_id را ارسال کنید.")
        return attrs


class SubmitPaymentSerializer(serializers.Serializer):
    receipt = serializers.FileField()
    tracking_code = serializers.CharField(max_length=100, required=False, allow_blank=True)
    note = serializers.CharField(max_length=500, required=False, allow_blank=True)


class PaymentOrderSerializer(serializers.ModelSerializer):
    product_title = serializers.SerializerMethodField()

    class Meta:
        model = PaymentOrder
        fields = [
            "id", "product_type", "product_title", "amount_irr", "status",
            "tracking_code", "user_note", "review_note", "created_at", "reviewed_at",
        ]
        read_only_fields = fields

    def get_product_title(self, obj):
        if obj.plan_id:
            return obj.plan.title
        if obj.exam_id:
            return obj.exam.title
        return ""


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ["id", "title", "period", "duration_days", "price_irr"]
