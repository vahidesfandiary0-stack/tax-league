from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.payments.models import BazaarPurchase, PaymentOrder
from apps.subscriptions.models import SubscriptionPlan, UserSubscription


class BazaarSubscriptionAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("09121110001")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.plan = SubscriptionPlan.objects.get(period=SubscriptionPlan.Period.MONTHLY)

    @patch("apps.payments.bazaar_views.ensure_bazaar_ready")
    def test_create_order_returns_server_owned_order(self, ensure_ready):
        response = self.client.post(
            "/api/v1/payments/bazaar/orders/",
            {"product_id": "raqtiva_monthly"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        order = PaymentOrder.objects.get(pk=response.data["id"])
        self.assertEqual(order.user_id, self.user.pk)
        self.assertEqual(order.plan_id, self.plan.pk)
        self.assertEqual(order.amount_irr, self.plan.price_irr)
        ensure_ready.assert_called_once()

    @patch("apps.payments.bazaar_views.verify_bazaar_subscription")
    def test_server_verification_activates_subscription_without_storing_raw_token(self, verify):
        order = PaymentOrder.objects.create(
            user=self.user,
            product_type=PaymentOrder.ProductType.SUBSCRIPTION,
            plan=self.plan,
            amount_irr=self.plan.price_irr,
        )
        expiry = timezone.now() + timedelta(days=30)
        verify.return_value = {
            "expires_at": expiry,
            "auto_renewing": True,
            "bazaar_order_id": "bazaar-order-1",
        }
        purchase_token = "opaque-sensitive-token"

        response = self.client.post(
            f"/api/v1/payments/bazaar/orders/{order.pk}/verify/",
            {"product_id": "raqtiva_monthly", "purchase_token": purchase_token},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["verified"])
        purchase = BazaarPurchase.objects.get(order=order)
        self.assertEqual(
            purchase.purchase_token_hash,
            BazaarPurchase.token_digest(purchase_token),
        )
        self.assertNotEqual(purchase.purchase_token_hash, purchase_token)
        self.assertTrue(UserSubscription.objects.filter(source_order=order, user=self.user).exists())
        order.refresh_from_db()
        self.assertEqual(order.status, PaymentOrder.Status.APPROVED)

    @patch("apps.payments.bazaar_views.verify_bazaar_subscription")
    def test_restore_refreshes_server_verified_expiry(self, verify):
        order = PaymentOrder.objects.create(
            user=self.user,
            product_type=PaymentOrder.ProductType.SUBSCRIPTION,
            plan=self.plan,
            amount_irr=self.plan.price_irr,
            status=PaymentOrder.Status.APPROVED,
        )
        token = "existing-purchase-token"
        old_expiry = timezone.now() + timedelta(days=2)
        new_expiry = timezone.now() + timedelta(days=30)
        BazaarPurchase.objects.create(
            order=order,
            user=self.user,
            product_id="raqtiva_monthly",
            purchase_token_hash=BazaarPurchase.token_digest(token),
            expires_at=old_expiry,
        )
        UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            starts_at=timezone.now(),
            ends_at=old_expiry,
            status=UserSubscription.Status.EXPIRED,
            source_order=order,
        )
        verify.return_value = {
            "expires_at": new_expiry,
            "auto_renewing": True,
            "bazaar_order_id": "bazaar-order-restored",
        }

        response = self.client.post(
            "/api/v1/payments/bazaar/restore/",
            {"product_id": "raqtiva_monthly", "purchase_token": token},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["restored"])
        restored_subscription = UserSubscription.objects.get(source_order=order)
        self.assertEqual(restored_subscription.ends_at, new_expiry)
        self.assertEqual(restored_subscription.status, UserSubscription.Status.ACTIVE)
