from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User


class AdminDashboardAccessTests(TestCase):
    def test_dashboard_redirects_anonymous_users(self):
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_is_available_to_staff_users(self):
        staff = User.objects.create_user(
            phone_number="09120000001",
            is_staff=True,
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد مدیریت")
