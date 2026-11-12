from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User


class AdminDashboardAccessTests(TestCase):
    def test_dashboard_redirects_anonymous_users(self):
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_is_superuser_only(self):
        staff = User.objects.create_user(phone_number="09120000001", is_staff=True)
        self.client.force_login(staff)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, 302)

        root = User.objects.create_superuser(phone_number="09120000002", password="unused")
        self.client.force_login(root)
        response = self.client.get(reverse("admin-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد مدیریت")

    def test_appeal_queue_requires_league_permission(self):
        staff = User.objects.create_user(phone_number="09120000003", is_staff=True)
        self.client.force_login(staff)
        response = self.client.get(reverse("admin-league-appeals"))
        self.assertEqual(response.status_code, 302)

    def test_superuser_can_open_appeal_queue(self):
        root = User.objects.create_superuser(phone_number="09120000004", password="unused")
        self.client.force_login(root)
        response = self.client.get(reverse("admin-league-appeals"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "بررسی اعتراض‌های لیگ")
