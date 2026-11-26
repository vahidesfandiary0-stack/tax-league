import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.payments.models import PaymentOrder
from apps.payments.services import (
    approve_order, create_subscription_order, get_payment_instructions,
    submit_payment,
)
from apps.subscriptions.models import SubscriptionPlan, UserSubscription


@pytest.mark.django_db
def test_manual_card_transfer_activates_subscription_only_after_admin_approval(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    user_model = get_user_model()
    user = user_model.objects.create_user(phone_number="09125550001")
    reviewer = user_model.objects.create_superuser(
        phone_number="09125550002", password="not-used"
    )
    plan = SubscriptionPlan.objects.create(
        title="اشتراک ماهانه", period=SubscriptionPlan.Period.MONTHLY,
        duration_days=30, price_irr=1_990_000,
    )

    order = create_subscription_order(user, plan.pk)
    assert order.amount_irr == 1_990_000
    assert order.status == PaymentOrder.Status.AWAITING_PAYMENT
    assert not UserSubscription.objects.filter(user=user).exists()

    receipt = SimpleUploadedFile(
        "receipt.png", b"\x89PNG\r\n\x1a\n" + b"test-image-bytes",
        content_type="image/png",
    )
    submitted = submit_payment(
        order.pk, user, receipt, tracking_code="TRACK-001", note="پرداخت اشتراک"
    )
    assert submitted.status == PaymentOrder.Status.UNDER_REVIEW
    assert not UserSubscription.objects.filter(user=user).exists()

    approved = approve_order(order.pk, reviewer)
    subscription = UserSubscription.objects.get(user=user, source_order=order)
    assert approved.status == PaymentOrder.Status.APPROVED
    assert subscription.plan_id == plan.pk
    assert subscription.starts_at <= timezone.now()
    assert subscription.ends_at - subscription.starts_at == timezone.timedelta(days=30)


@pytest.mark.django_db
def test_payment_instructions_are_hidden_until_admin_configures_card():
    from apps.payments.models import PaymentSettings

    assert get_payment_instructions() is None
    PaymentSettings.objects.create(card_number="6037-0000-0000-0000", account_holder="صاحب حساب")
    assert get_payment_instructions() == {
        "card_number": "6037-0000-0000-0000",
        "account_holder": "صاحب حساب",
    }
