from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscriptions.models import SubscriptionPlan
from apps.exams.models import Exam
from .models import PaymentOrder
from .serializers import (
    CreateOrderSerializer, PaymentOrderSerializer, SubmitPaymentSerializer,
    SubscriptionPlanSerializer,
)
from .services import (
    create_exam_order, create_subscription_order, get_payment_instructions,
    submit_payment,
)


def service_error(exc):
    return ValidationError({"detail": exc.messages if hasattr(exc, "messages") else str(exc)})


class SubscriptionPlanListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.filter(is_active=True)


class PaymentInstructionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        instructions = get_payment_instructions()
        if not instructions:
            return Response({"configured": False, "detail": "اطلاعات پرداخت هنوز توسط مدیر تنظیم نشده است."})
        return Response({"configured": True, **instructions})


class PaymentOrderListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentOrderSerializer

    def get_queryset(self):
        return PaymentOrder.objects.filter(user=self.request.user).select_related("plan", "exam")


class CreatePaymentOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            if data["product_type"] == PaymentOrder.ProductType.SUBSCRIPTION:
                order = create_subscription_order(request.user, data["plan_id"])
            else:
                order = create_exam_order(request.user, data["exam_id"])
        except (DjangoValidationError, SubscriptionPlan.DoesNotExist, Exam.DoesNotExist) as exc:
            raise service_error(exc)
        return Response(PaymentOrderSerializer(order).data, status=status.HTTP_201_CREATED)


class SubmitPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, order_id):
        serializer = SubmitPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            order = submit_payment(
                order_id, request.user, data["receipt"],
                data.get("tracking_code", ""), data.get("note", ""),
            )
        except (DjangoValidationError, PaymentOrder.DoesNotExist) as exc:
            raise service_error(exc)
        return Response(PaymentOrderSerializer(order).data)


class PaymentOrderDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentOrderSerializer
    lookup_url_kwarg = "order_id"

    def get_queryset(self):
        return PaymentOrder.objects.filter(user=self.request.user).select_related("plan", "exam")
