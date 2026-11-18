from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.payments.models import PaymentOrder
from apps.payments.services import approve_order, create_subscription_order, submit_payment
from apps.subscriptions.access import has_active_academy_access
from apps.subscriptions.models import SubscriptionPlan, UserSubscription


class SubscriptionPurchaseFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("09120000031")
        self.admin = User.objects.create_superuser("09120000032", password="test-only-password")
        self.plan = SubscriptionPlan.objects.create(
            title="اشتراک آزمایشی",
            period=SubscriptionPlan.Period.MONTHLY,
            duration_days=30,
            price_irr=250000,
        )

    def test_order_receipt_admin_approval_activates_subscription_once(self):
        order = create_subscription_order(self.user, self.plan.pk)
        self.assertEqual(order.status, PaymentOrder.Status.AWAITING_PAYMENT)
        self.assertEqual(order.amount_irr, self.plan.price_irr)
        self.assertFalse(has_active_academy_access(self.user))

        receipt = SimpleUploadedFile(
            "receipt.png",
            b"\x89PNG\r\n\x1a\n" + b"valid-test-png-payload",
            content_type="image/png",
        )
        submitted = submit_payment(order.pk, self.user, receipt, "TRACK-123")
        self.assertEqual(submitted.status, PaymentOrder.Status.UNDER_REVIEW)
        self.assertEqual(submitted.tracking_code, "TRACK-123")

        approved = approve_order(order.pk, self.admin)
        self.assertEqual(approved.status, PaymentOrder.Status.APPROVED)
        self.assertEqual(UserSubscription.objects.filter(source_order=order).count(), 1)
        self.assertTrue(has_active_academy_access(self.user))
        subscription = UserSubscription.objects.get(source_order=order)
        self.assertEqual(subscription.ends_at - subscription.starts_at, timedelta(days=30))

        with self.assertRaises(ValidationError):
            approve_order(order.pk, self.admin)
        self.assertEqual(UserSubscription.objects.filter(source_order=order).count(), 1)

    def test_receipt_upload_cannot_submit_another_users_order(self):
        other = User.objects.create_user("09120000033")
        order = create_subscription_order(other, self.plan.pk)
        receipt = SimpleUploadedFile(
            "receipt.png",
            b"\x89PNG\r\n\x1a\n" + b"valid-test-png-payload",
            content_type="image/png",
        )
        with self.assertRaises(PaymentOrder.DoesNotExist):
            submit_payment(order.pk, self.user, receipt)

    def test_receipt_size_and_content_are_validated(self):
        order = create_subscription_order(self.user, self.plan.pk)
        oversized = SimpleUploadedFile(
            "receipt.png",
            b"\x89PNG\r\n\x1a\n" + (b"x" * (5 * 1024 * 1024)),
            content_type="image/png",
        )
        with self.assertRaises(ValidationError):
            submit_payment(order.pk, self.user, oversized)

        invalid = SimpleUploadedFile(
            "receipt.png", b"not-a-real-png", content_type="image/png"
        )
        with self.assertRaises(ValidationError):
            submit_payment(order.pk, self.user, invalid)



    def test_payment_order_cannot_be_approved_by_direct_model_save(self):
        order = create_subscription_order(self.user, self.plan.pk)
        order.status = PaymentOrder.Status.APPROVED
        with self.assertRaises(ValidationError):
            order.save()

    def test_payment_order_cannot_skip_receipt_review(self):
        order = create_subscription_order(self.user, self.plan.pk)
        order.status = PaymentOrder.Status.APPROVED
        order.reviewer = self.admin
        order.reviewed_at = timezone.now()
        with self.assertRaises(ValidationError):
            order.save()
