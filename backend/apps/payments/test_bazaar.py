from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from .bazaar import BazaarConfigurationError, BazaarVerificationError, verify_bazaar_subscription


@override_settings(
    BAZAAR_CLIENT_ID="client",
    BAZAAR_CLIENT_SECRET="secret",
    BAZAAR_REFRESH_TOKEN="refresh",
    BAZAAR_PACKAGE_NAME="ir.raqtiva.tax_league",
)
class BazaarVerificationTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    @patch("apps.payments.bazaar._request_json")
    def test_valid_paid_subscription_returns_server_expiry(self, request_json):
        expiry = int((timezone.now() + timedelta(days=30)).timestamp() * 1000)
        request_json.side_effect = [
            {"access_token": "server-token", "expires_in": 3600},
            {"paymentState": 1, "expiryTimeMillis": expiry, "autoRenewing": True, "orderId": "bazaar-order"},
        ]
        result = verify_bazaar_subscription("raqtiva_monthly", "opaque-purchase-token")
        self.assertGreater(result["expires_at"], timezone.now())
        self.assertTrue(result["auto_renewing"])
        self.assertEqual(result["bazaar_order_id"], "bazaar-order")
        self.assertEqual(request_json.call_count, 2)

    @patch("apps.payments.bazaar._request_json")
    def test_pending_payment_is_rejected(self, request_json):
        request_json.side_effect = [
            {"access_token": "server-token", "expires_in": 3600},
            {"paymentState": 0, "expiryTimeMillis": 9999999999999},
        ]
        with self.assertRaises(BazaarVerificationError):
            verify_bazaar_subscription("raqtiva_monthly", "token")

    @patch("apps.payments.bazaar._request_json")
    def test_expired_subscription_is_rejected(self, request_json):
        request_json.side_effect = [
            {"access_token": "server-token", "expires_in": 3600},
            {"paymentState": 1, "expiryTimeMillis": 1},
        ]
        with self.assertRaises(BazaarVerificationError):
            verify_bazaar_subscription("raqtiva_monthly", "token")

    @override_settings(BAZAAR_REFRESH_TOKEN="")
    def test_missing_server_credentials_fail_closed(self):
        with self.assertRaises(BazaarConfigurationError):
            verify_bazaar_subscription("raqtiva_monthly", "token")
