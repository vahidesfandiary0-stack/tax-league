from pathlib import Path

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import FileResponse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscriptions.models import SubscriptionPlan, UserSubscription
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


class MySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        now = timezone.now()
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status=UserSubscription.Status.ACTIVE,
            starts_at__lte=now,
            ends_at__gt=now,
        ).select_related("plan").order_by("-ends_at").first()
        if not subscription:
            return Response({"active": False, "ends_at": None, "plan": None})
        return Response({
            "active": True,
            "plan": subscription.plan.title,
            "starts_at": subscription.starts_at,
            "ends_at": subscription.ends_at,
        })


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


class AdminReceiptDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        if not (
            request.user.is_superuser
            or (request.user.is_staff and request.user.has_perm("payments.view_paymentorder"))
        ):
            raise PermissionDenied("فقط مسئولان مجاز پرداخت به رسیدها دسترسی دارند.")
        try:
            order = PaymentOrder.objects.get(pk=order_id)
        except PaymentOrder.DoesNotExist:
            return Response({"detail": "سفارش پیدا نشد."}, status=404)
        if not order.receipt:
            return Response({"detail": "رسیدی برای این سفارش ثبت نشده است."}, status=404)
        return FileResponse(
            order.receipt.open("rb"),
            as_attachment=True,
            filename=Path(order.receipt.name).name,
        )


class PaymentOrderDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentOrderSerializer
    lookup_url_kwarg = "order_id"

    def get_queryset(self):
        return PaymentOrder.objects.filter(user=self.request.user).select_related("plan", "exam")
