from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.payments.models import PaymentOrder
from apps.subscriptions.models import SubscriptionPlan, UserSubscription
from .models import AcademyContent


class AcademySubscriptionAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("09120000991")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.content = AcademyContent.objects.create(
            slug="tax-trap-basics",
            title="مبانی تله‌شناسی مالیاتی",
            summary="نمونه محتوای آزمایشی",
            category=AcademyContent.Category.TRAPOLOGY,
            body="متن اختصاصی آموزشی",
            source_title="منبع رسمی آزمایشی",
            source_url="https://regulation.tax.gov.ir/",
            is_exclusive=True,
            is_active=True,
        )

    def _activate_subscription(self):
        plan = SubscriptionPlan.objects.create(
            title="ماهانه",
            period=SubscriptionPlan.Period.MONTHLY,
            duration_days=30,
            price_irr=1_990_000,
        )
        order = PaymentOrder.objects.create(
            user=self.user,
            product_type=PaymentOrder.ProductType.SUBSCRIPTION,
            plan=plan,
            amount_irr=plan.price_irr,
            status=PaymentOrder.Status.APPROVED,
        )
        UserSubscription.objects.create(
            user=self.user,
            plan=plan,
            starts_at=timezone.now() - timedelta(minutes=1),
            ends_at=timezone.now() + timedelta(days=30),
            source_order=order,
        )

    def test_exclusive_list_is_visible_as_locked_teaser_without_subscription(self):
        response = self.client.get("/api/v1/academy/content/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["has_active_subscription"])
        item = response.data["results"][0]
        self.assertTrue(item["is_locked"])
        self.assertIsNone(item["source_title"])
        self.assertNotIn("body", item)

    def test_exclusive_detail_is_denied_without_active_subscription(self):
        response = self.client.get("/api/v1/academy/content/tax-trap-basics/")
        self.assertEqual(response.status_code, 403)

    def test_active_subscriber_can_read_exclusive_content_and_source(self):
        self._activate_subscription()
        response = self.client.get("/api/v1/academy/content/tax-trap-basics/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["body"], "متن اختصاصی آموزشی")
        self.assertEqual(response.data["source_url"], "https://regulation.tax.gov.ir/")

    def test_expired_subscription_does_not_unlock_exclusive_content(self):
        plan = SubscriptionPlan.objects.create(
            title="سه‌ماهه",
            period=SubscriptionPlan.Period.QUARTERLY,
            duration_days=90,
            price_irr=4_990_000,
        )
        order = PaymentOrder.objects.create(
            user=self.user,
            product_type=PaymentOrder.ProductType.SUBSCRIPTION,
            plan=plan,
            amount_irr=plan.price_irr,
            status=PaymentOrder.Status.APPROVED,
        )
        UserSubscription.objects.create(
            user=self.user,
            plan=plan,
            starts_at=timezone.now() - timedelta(days=100),
            ends_at=timezone.now() - timedelta(days=10),
            status=UserSubscription.Status.EXPIRED,
            source_order=order,
        )
        response = self.client.get("/api/v1/academy/content/tax-trap-basics/")
        self.assertEqual(response.status_code, 403)

    def test_free_content_remains_accessible_without_subscription(self):
        self.content.is_exclusive = False
        self.content.save(update_fields=["is_exclusive"])
        response = self.client.get("/api/v1/academy/content/tax-trap-basics/")
        self.assertEqual(response.status_code, 200)
