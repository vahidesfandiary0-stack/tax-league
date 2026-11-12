from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .otp import issue_challenge, verify_challenge
from .serializers import RequestOTPSerializer, VerifyOTPSerializer
from .sms import SMSDeliveryError, SMSDeliveryNotConfigured, send_login_code

User = get_user_model()


class RequestOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "otp_request"

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]
        ip = request.META.get("REMOTE_ADDR")

        challenge = None
        try:
            challenge, code = issue_challenge(phone, ip)
            send_login_code(phone, code)
        except SMSDeliveryError as exc:
            if challenge is not None:
                challenge.consumed_at = timezone.now()
                challenge.save(update_fields=["consumed_at"])
            detail = (
                "ارسال پیامک هنوز پیکربندی نشده است."
                if isinstance(exc, SMSDeliveryNotConfigured)
                else "ارسال پیامک در حال حاضر ممکن نیست؛ دوباره تلاش کنید."
            )
            return Response(
                {"detail": detail},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {"detail": "اگر شماره معتبر باشد، کد ورود ارسال می‌شود."},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "otp_verify"

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        with transaction.atomic():
            if not verify_challenge(phone, code):
                return Response(
                    {"detail": "کد نامعتبر یا منقضی شده است."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user, _ = User.objects.get_or_create(phone_number=phone)
            token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": {
                "id": user.pk,
                "phone_number": user.phone_number,
                "display_name": user.display_name,
            },
        })
