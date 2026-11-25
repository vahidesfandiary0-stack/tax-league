from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from .models import SubscriptionPlan


class SubscriptionPlanAvailabilityTests(TestCase):
    def test_default_bazaar_plans_are_seeded_with_approved_prices(self):
        expected = {
            "monthly": (30, 1_990_000),
            "quarterly": (90, 4_990_000),
            "annual": (365, 14_990_000),
        }
        for period, values in expected.items():
            plan = SubscriptionPlan.objects.get(period=period, is_active=True)
            self.assertEqual((plan.duration_days, plan.price_irr), values)

    def test_authenticated_plan_endpoint_exposes_all_three_bazaar_plans(self):
        user = User.objects.create_user("09120000992")
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/v1/payments/plans/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {item["period"] for item in response.data},
            {"monthly", "quarterly", "annual"},
        )
