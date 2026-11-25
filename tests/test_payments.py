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
        self.assertEqual(order.plan_duration_days_snapshot, 30)
        order.amount_irr = 1
        with self.assertRaises(ValidationError):
            order.save()

    def test_approval_grants_subscription_once(self):
        order = create_subscription_order(self.user, self.plan.pk)
        order.status = PaymentOrder.Status.UNDER_REVIEW
        order.receipt = SimpleUploadedFile(
            "receipt.pdf", b"%PDF-1.4\nreceipt\n%%EOF", content_type="application/pdf"
        )
        order.save()
        self.plan.duration_days = 90
        self.plan.save(update_fields=["duration_days"])
        approved = approve_order(order.pk, self.admin)
        self.assertEqual(approved.status, PaymentOrder.Status.APPROVED)
        self.assertEqual(UserSubscription.objects.filter(source_order=order).count(), 1)
        subscription = UserSubscription.objects.get(source_order=order)
        self.assertEqual(subscription.ends_at - subscription.starts_at, timedelta(days=30))
        with self.assertRaises(ValidationError):
            approve_order(order.pk, self.admin)
        self.assertEqual(UserSubscription.objects.filter(source_order=order).count(), 1)

    def test_card_settings_singleton(self):
        first = PaymentSettings.objects.create(card_number="1111222233334444")
        second = PaymentSettings.objects.create(card_number="5555666677778888")
        self.assertEqual(PaymentSettings.objects.count(), 1)
        self.assertEqual(PaymentSettings.objects.get().card_number, "5555666677778888")


class PaymentApiWorkflowTests(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            phone_number="09120000004", display_name="کاربر پرداخت"
        )
        self.other_user = get_user_model().objects.create_user(
            phone_number="09120000005", display_name="کاربر دیگر"
        )
        self.plan = SubscriptionPlan.objects.create(
            title="اشتراک آزمایشی", period=SubscriptionPlan.Period.MONTHLY,
            duration_days=30, price_irr=1990000,
        )
        PaymentSettings.objects.create(
            card_number="1111222233334444", account_holder="صاحب حساب"
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_card_instructions_and_plan_listing(self):
        response = self.client.get("/api/v1/payments/instructions/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["card_number"], "1111222233334444")
        plans = self.client.get("/api/v1/payments/plans/")
        self.assertEqual(plans.status_code, 200)
        self.assertEqual(plans.data[0]["price_irr"], 1990000)

    def test_complete_order_and_receipt_submission(self):
        created = self.client.post("/api/v1/payments/orders/create/", {
            "product_type": "subscription", "plan_id": str(self.plan.pk),
        }, format="json")
        self.assertEqual(created.status_code, 201)
        order_id = created.data["id"]
        receipt = SimpleUploadedFile(
            "transfer.pdf", b"%PDF-1.4\nreceipt\n%%EOF", content_type="application/pdf"
        )
        submitted = self.client.post(
            f"/api/v1/payments/orders/{order_id}/submit/",
            {"receipt": receipt, "tracking_code": "TRX-123"},
            format="multipart",
        )
        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(submitted.data["status"], PaymentOrder.Status.UNDER_REVIEW)
        self.assertNotIn("receipt", submitted.data)

    def test_user_cannot_submit_receipt_to_another_users_order(self):
        order = create_subscription_order(self.other_user, self.plan.pk)
        receipt = SimpleUploadedFile(
            "transfer.pdf", b"%PDF-1.4\nreceipt\n%%EOF", content_type="application/pdf"
        )
        response = self.client.post(
            f"/api/v1/payments/orders/{order.pk}/submit/",
            {"receipt": receipt}, format="multipart",
        )
        self.assertEqual(response.status_code, 404)
