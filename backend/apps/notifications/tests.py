from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.test import APITestCase

from .admin import ShowcaseSlideAdmin
from .models import ShowcaseSlide


class ShowcaseSlideApiTests(APITestCase):
    def setUp(self):
        # Migration 0003 seeds founder/logo defaults; clear them so each API
        # test controls its own slide fixtures and can test the empty response.
        ShowcaseSlide.objects.all().delete()
        self.user = get_user_model().objects.create_user(phone_number="09120000001")
        self.url = "/api/v1/notifications/showcase/"

    def test_showcase_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_receives_only_active_in_window_slides_in_order(self):
        now = timezone.now()
        later = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.ADVERTISEMENT,
            title="تبلیغ آینده",
            body="نباید هنوز نمایش داده شود",
            starts_at=now + timedelta(hours=1),
            sort_order=0,
        )
        inactive = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.MESSAGE,
            title="غیرفعال",
            body="نباید نمایش داده شود",
            is_active=False,
            sort_order=1,
        )
        second = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.ADVERTISEMENT,
            title="تبلیغ دوم",
            body="متن تبلیغ دوم",
            duration_seconds=7,
            sort_order=0,
        )
        founder = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.FOUNDER,
            title="بنیان‌گذار لیگ: وحید اسفندیاری",
            body="حسابرس ارشد اداره کل امورمالیاتی خوزستان",
            duration_seconds=6,
            sort_order=1,
        )
        last = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.MESSAGE,
            title="پیام اول",
            body="متن پیام اول",
            sort_order=10,
        )
        countdown = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.EXAM_COUNTDOWN,
            title="تا شروع رقابت رسمی",
            body="برای آزمون آماده شوید",
            image_url="https://cdn.example.test/countdown.png",
            duration_seconds=11,
            sort_order=2,
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.data],
            [second.pk, founder.pk, countdown.pk, last.pk],
        )
        self.assertEqual(response.data[0]["duration_seconds"], 7)
        self.assertEqual(response.data[1]["duration_seconds"], 6)
        self.assertEqual(response.data[1]["title"], "بنیان‌گذار لیگ: وحید اسفندیاری")
        self.assertEqual(
            response.data[1]["body"],
            "حسابرس ارشد اداره کل امورمالیاتی خوزستان",
        )
        self.assertEqual(response.data[2]["kind"], ShowcaseSlide.Kind.EXAM_COUNTDOWN)
        self.assertEqual(response.data[2]["title"], "تا شروع رقابت رسمی")
        self.assertEqual(response.data[2]["body"], "برای آزمون آماده شوید")
        self.assertEqual(response.data[2]["image_url"], "https://cdn.example.test/countdown.png")
        self.assertEqual(response.data[2]["duration_seconds"], 11)
        self.assertNotIn(later.pk, [item["id"] for item in response.data])
        self.assertNotIn(inactive.pk, [item["id"] for item in response.data])

    def test_staff_manager_can_manage_all_showcase_slides(self):
        manager = get_user_model().objects.create_user(
            phone_number="09120000002",
            is_staff=True,
        )
        request = RequestFactory().get("/admin/notifications/showcaseslide/")
        request.user = manager
        model_admin = ShowcaseSlideAdmin(ShowcaseSlide, admin.site)

        self.assertTrue(model_admin.has_module_permission(request))
        self.assertTrue(model_admin.has_view_permission(request))
        self.assertTrue(model_admin.has_add_permission(request))
        self.assertTrue(model_admin.has_change_permission(request))
        self.assertTrue(model_admin.has_delete_permission(request))
        editable_fields = {
            field
            for section in model_admin.fieldsets
            for field in section[1]["fields"]
        }
        self.assertTrue({
            "kind", "title", "body", "image", "image_url",
            "is_active", "sort_order", "duration_seconds",
            "starts_at", "ends_at",
        }.issubset(editable_fields))

    def test_authenticated_user_can_receive_empty_successful_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
