from datetime import timedelta
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.exams.models import Exam
from apps.payments.models import PaymentOrder, PaymentSettings
from apps.payments.services import approve_order, create_subscription_order
from apps.subscriptions.models import SubscriptionPlan, UserSubscription


class PaymentWorkflowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            phone_number="09120000002", display_name="خریدار"
        )
        self.admin = get_user_model().objects.create_superuser(
            phone_number="09120000003", password="test-password"
        )
        self.plan = SubscriptionPlan.objects.create(
            title="اشتراک ماهانه", period=SubscriptionPlan.Period.MONTHLY,
            duration_days=30, price_irr=1000000,
        )

    def test_order_captures_server_price_and_is_immutable(self):
        order = create_subscription_order(self.user, self.plan.pk)
        self.assertEqual(order.amount_irr, self.plan.price_irr)
        order.amount_irr = 1
        with self.assertRaises(ValidationError):
            order.save()

    def test_approval_grants_subscription_once(self):
        order = create_subscription_order(self.user, self.plan.pk)
        order.status = PaymentOrder.Status.UNDER_REVIEW
        order.receipt = SimpleUploadedFile(
            "receipt.png", b"\x89PNG\r\n\x1a\ncontent", content_type="image/png"
        )
        order.save()
        approved = approve_order(order.pk, self.admin)
        self.assertEqual(approved.status, PaymentOrder.Status.APPROVED)
        self.assertEqual(UserSubscription.objects.filter(source_order=order).count(), 1)
        with self.assertRaises(ValidationError):
            approve_order(order.pk, self.admin)
        self.assertEqual(UserSubscription.objects.filter(source_order=order).count(), 1)

    def test_card_settings_singleton(self):
        first = PaymentSettings.objects.create(card_number="1111222233334444")
        second = PaymentSettings.objects.create(card_number="5555666677778888")
        self.assertEqual(PaymentSettings.objects.count(), 1)
        self.assertEqual(PaymentSettings.objects.get().card_number, "5555666677778888")
