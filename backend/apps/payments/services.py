from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import PaymentOrder, PaymentSettings, PurchasedExamAccess


@transaction.atomic
def create_subscription_order(user, plan_id):
    from apps.subscriptions.models import SubscriptionPlan
    plan = SubscriptionPlan.objects.get(pk=plan_id, is_active=True)
    return PaymentOrder.objects.create(
        user=user, product_type=PaymentOrder.ProductType.SUBSCRIPTION,
        plan=plan, amount_irr=plan.price_irr,
    )


@transaction.atomic
def create_exam_order(user, exam_id):
    from apps.exams.models import Exam
    exam = Exam.objects.get(pk=exam_id, status=Exam.Status.PUBLISHED)
    if not exam.requires_purchase:
        raise ValidationError("این آزمون نیازی به خرید ندارد.")
    if exam.price_irr < 1:
        raise ValidationError("مبلغ خرید این آزمون هنوز توسط مدیر تنظیم نشده است.")
    from .models import PurchasedExamAccess
    if PurchasedExamAccess.objects.filter(user=user, exam=exam).exists():
        raise ValidationError("شما قبلاً به این آزمون دسترسی خریده‌اید.")
    # Exam price is captured from the published exam and cannot be changed on the order.
    return PaymentOrder.objects.create(
        user=user, product_type=PaymentOrder.ProductType.EXAM,
        exam=exam, amount_irr=exam.price_irr,
    )


@transaction.atomic
def submit_payment(order_id, user, receipt, tracking_code="", note=""):
    order = PaymentOrder.objects.select_for_update().get(pk=order_id, user=user)
    if order.status not in (PaymentOrder.Status.AWAITING_PAYMENT, PaymentOrder.Status.REJECTED):
        raise ValidationError("این سفارش در وضعیت قابل ارسال رسید نیست.")
    if not receipt:
        raise ValidationError("تصویر یا فایل رسید الزامی است.")
    for validator in PaymentOrder._meta.get_field("receipt").validators:
        validator(receipt)
    order.receipt = receipt
    order.tracking_code = tracking_code.strip()[:100]
    order.user_note = note.strip()[:500]
    order.status = PaymentOrder.Status.UNDER_REVIEW
    order.reviewer = None
    order.review_note = ""
    order.reviewed_at = None
    order.save()
    return order


@transaction.atomic
def approve_order(order_id, reviewer):
    order = PaymentOrder.objects.select_for_update().select_related("user", "plan", "exam").get(pk=order_id)
    if order.status != PaymentOrder.Status.UNDER_REVIEW:
        raise ValidationError("فقط سفارش در انتظار بررسی قابل تأیید است.")
    now = timezone.now()
    if order.product_type == PaymentOrder.ProductType.SUBSCRIPTION:
        from apps.subscriptions.models import UserSubscription
        latest = UserSubscription.objects.select_for_update().filter(
            user=order.user, status=UserSubscription.Status.ACTIVE, ends_at__gt=now
        ).order_by("-ends_at").first()
        starts_at = latest.ends_at if latest else now
        UserSubscription.objects.create(
            user=order.user, plan=order.plan, starts_at=starts_at,
            ends_at=starts_at + timedelta(days=order.plan.duration_days),
            source_order=order,
        )
    else:
        PurchasedExamAccess.objects.create(user=order.user, exam=order.exam, source_order=order)
    order.status = PaymentOrder.Status.APPROVED
    order.reviewer = reviewer
    order.review_note = "پرداخت تأیید شد."
    order.reviewed_at = now
    order.save(update_fields=["status", "reviewer", "review_note", "reviewed_at", "updated_at"])
    from apps.notifications.models import Notification
    from apps.notifications.services import create_notification
    create_notification(
        recipient=order.user, kind=Notification.Kind.PAYMENT_APPROVED,
        title="پرداخت تأیید شد", body="پرداخت شما با موفقیت تأیید شد.",
        data={"order_id": str(order.pk), "product_type": order.product_type},
    )
    if order.product_type == PaymentOrder.ProductType.SUBSCRIPTION:
        create_notification(
            recipient=order.user, kind=Notification.Kind.SUBSCRIPTION_ACTIVATED,
            title="اشتراک فعال شد", body="اشتراک شما فعال شده و اکنون قابل استفاده است.",
            data={"order_id": str(order.pk)},
        )
    return order


@transaction.atomic
def reject_order(order_id, reviewer, reason):
    order = PaymentOrder.objects.select_for_update().get(pk=order_id)
    if order.status != PaymentOrder.Status.UNDER_REVIEW:
        raise ValidationError("فقط سفارش در انتظار بررسی قابل رد است.")
    order.status = PaymentOrder.Status.REJECTED
    order.reviewer = reviewer
    order.review_note = reason.strip()[:500] or "رسید تأیید نشد."
    order.reviewed_at = timezone.now()
    order.save(update_fields=["status", "reviewer", "review_note", "reviewed_at", "updated_at"])
    from apps.notifications.models import Notification
    from apps.notifications.services import create_notification
    create_notification(
        recipient=order.user, kind=Notification.Kind.PAYMENT_REJECTED,
        title="پرداخت تأیید نشد",
        body="رسید پرداخت شما تأیید نشد. لطفاً جزئیات سفارش را بررسی و در صورت نیاز دوباره ارسال کنید.",
        data={"order_id": str(order.pk)},
    )
    return order


def get_payment_instructions():
    settings = PaymentSettings.objects.filter(pk=1).first()
    if not settings or not settings.card_number:
        return None
    return {"card_number": settings.card_number, "account_holder": settings.account_holder}
