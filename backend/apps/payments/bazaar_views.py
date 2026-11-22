from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscriptions.models import SubscriptionPlan, UserSubscription
from .bazaar import BazaarConfigurationError, BazaarVerificationError, ensure_bazaar_ready, verify_bazaar_subscription
from .models import BazaarPurchase, PaymentOrder


PRODUCT_IDS = {"monthly": "raqtiva_monthly", "quarterly": "raqtiva_quarterly", "annual": "raqtiva_annual"}


class BazaarServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "سرویس تأیید پرداخت کافه‌بازار در حال حاضر آماده نیست."
    default_code = "bazaar_unavailable"


def _verify_and_activate(order, user, product_id, purchase_token):
    if not isinstance(purchase_token, str) or not purchase_token.strip() or len(purchase_token) > 4096:
        raise ValidationError({"purchase_token": "توکن خرید معتبر نیست."})
    expected = PRODUCT_IDS.get(order.plan.period) if order.plan_id else None
    if order.user_id != user.id or order.product_type != PaymentOrder.ProductType.SUBSCRIPTION:
        raise NotFound("سفارش اشتراک پیدا نشد.")
    if product_id != expected:
        raise ValidationError({"product_id": "شناسه محصول با طرح سفارش مطابقت ندارد."})
    try:
        verified = verify_bazaar_subscription(product_id, purchase_token)
    except BazaarConfigurationError as exc:
        raise BazaarServiceUnavailable(str(exc)) from exc
    except BazaarVerificationError as exc:
        raise ValidationError({"detail": str(exc)}) from exc

    digest = BazaarPurchase.token_digest(purchase_token)
    if BazaarPurchase.objects.filter(purchase_token_hash=digest).exclude(order=order).exists():
        raise ValidationError("این توکن خرید قبلاً برای سفارش دیگری ثبت شده است.")

    with transaction.atomic():
        locked = PaymentOrder.objects.select_for_update().select_related("plan").get(pk=order.pk)
        if locked.status not in (
            PaymentOrder.Status.AWAITING_PAYMENT,
            PaymentOrder.Status.REJECTED,
            PaymentOrder.Status.APPROVED,
        ):
            raise ValidationError("این سفارش در وضعیت قابل تأیید نیست.")
        purchase = BazaarPurchase.objects.filter(order=locked).first()
        if locked.status == PaymentOrder.Status.APPROVED and not purchase:
            raise ValidationError("وضعیت سفارش با سابقه فعال‌سازی اشتراک سازگار نیست.")
        if locked.status == PaymentOrder.Status.APPROVED and not purchase:
            raise ValidationError("وضعیت سفارش با سابقه فعال‌سازی اشتراک سازگار نیست.")
        if purchase and purchase.purchase_token_hash != digest:
            raise ValidationError("این سفارش قبلاً به توکن خرید دیگری متصل شده است.")
        if purchase:
            purchase.expires_at = verified["expires_at"]
            purchase.auto_renewing = verified["auto_renewing"]
            purchase.bazaar_order_id = verified["bazaar_order_id"]
            purchase.save(update_fields=["expires_at", "auto_renewing", "bazaar_order_id", "verified_at"])
            subscription = UserSubscription.objects.get(source_order=locked)
            subscription.ends_at = verified["expires_at"]
            subscription.save(update_fields=["ends_at"])
        else:
            try:
                BazaarPurchase.objects.create(
                    order=locked, user=user, product_id=product_id,
                    purchase_token_hash=digest, bazaar_order_id=verified["bazaar_order_id"],
                    expires_at=verified["expires_at"], auto_renewing=verified["auto_renewing"],
                )
            except IntegrityError as exc:
                raise ValidationError("این توکن خرید قبلاً ثبت شده است.") from exc
            subscription = UserSubscription.objects.create(
                user=user, plan=locked.plan, starts_at=timezone.now(),
                ends_at=verified["expires_at"], source_order=locked,
            )
        locked.status = PaymentOrder.Status.APPROVED
        locked.review_note = "پرداخت اشتراک توسط API کافه‌بازار تأیید شد."
        locked.reviewed_at = timezone.now()
        locked.save(update_fields=["status", "review_note", "reviewed_at", "updated_at"])
        return subscription


class BazaarCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            ensure_bazaar_ready()
        except BazaarConfigurationError as exc:
            raise BazaarServiceUnavailable(str(exc)) from exc
        except BazaarVerificationError as exc:
            raise BazaarServiceUnavailable(str(exc)) from exc
        product_id = request.data.get("product_id")
        if product_id not in PRODUCT_IDS.values():
            raise ValidationError({"product_id": "شناسه محصول کافه‌بازار معتبر نیست."})
        period = next(key for key, value in PRODUCT_IDS.items() if value == product_id)
        plan = get_object_or_404(SubscriptionPlan, period=period, is_active=True)
        order = PaymentOrder.objects.create(
            user=request.user, product_type=PaymentOrder.ProductType.SUBSCRIPTION,
            plan=plan, amount_irr=plan.price_irr,
        )
        return Response({"id": str(order.pk), "product_id": product_id}, status=status.HTTP_201_CREATED)


class BazaarVerifyOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(PaymentOrder.objects.select_related("plan"), pk=order_id, user=request.user)
        subscription = _verify_and_activate(
            order, request.user, request.data.get("product_id"), request.data.get("purchase_token"),
        )
        return Response({"verified": True, "active": subscription.ends_at > timezone.now(),
                         "plan": subscription.plan.title, "ends_at": subscription.ends_at})


class BazaarRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id, token = request.data.get("product_id"), request.data.get("purchase_token")
        if not isinstance(token, str) or not token.strip():
            raise ValidationError({"purchase_token": "توکن خرید الزامی است."})
        digest = BazaarPurchase.token_digest(token)
        purchase = BazaarPurchase.objects.select_related("order__plan").filter(
            purchase_token_hash=digest, user=request.user, product_id=product_id,
        ).first()
        if not purchase:
            raise NotFound("خریدی با این توکن برای حساب فعلی ثبت نشده است.")
        subscription = _verify_and_activate(purchase.order, request.user, product_id, token)
        return Response({"restored": True, "active": subscription.ends_at > timezone.now(),
                         "plan": subscription.plan.title, "ends_at": subscription.ends_at})
