import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.exams.models import Exam

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
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.data],
            [second.pk, founder.pk, last.pk],
        )
        self.assertEqual(response.data[0]["duration_seconds"], 7)
        self.assertEqual(response.data[1]["duration_seconds"], 6)
        self.assertEqual(response.data[1]["title"], "بنیان‌گذار لیگ: وحید اسفندیاری")
        self.assertEqual(
            response.data[1]["body"],
            "حسابرس ارشد اداره کل امورمالیاتی خوزستان",
        )
        self.assertNotIn(later.pk, [item["id"] for item in response.data])
        self.assertNotIn(inactive.pk, [item["id"] for item in response.data])

    def test_authenticated_user_can_receive_empty_successful_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


    def test_countdown_uses_nearest_published_official_future_exam(self):
        now = timezone.now()
        countdown = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.EXAM_COUNTDOWN,
            title="شمارش معکوس",
            sort_order=2,
        )
        nearest = Exam.objects.create(
            title="آزمون رسمی نزدیک",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.PUBLISHED,
            counts_for_league=True,
            starts_at=now + timedelta(hours=3),
        )
        Exam.objects.create(
            title="آزمون رسمی دورتر",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.PUBLISHED,
            counts_for_league=True,
            starts_at=now + timedelta(days=2),
        )
        Exam.objects.create(
            title="آزمون تمرینی",
            kind=Exam.Kind.DAILY,
            status=Exam.Status.PUBLISHED,
            counts_for_league=False,
            starts_at=now + timedelta(minutes=30),
        )
        Exam.objects.create(
            title="آزمون پیش‌نویس",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.DRAFT,
            counts_for_league=True,
            starts_at=now + timedelta(minutes=15),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], countdown.pk)
        self.assertEqual(response.data[0]["exam_title"], nearest.title)
        self.assertEqual(response.data[0]["starts_at"], nearest.starts_at)

    def test_countdown_is_hidden_without_eligible_official_future_exam(self):
        now = timezone.now()
        countdown = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.EXAM_COUNTDOWN,
            title="شمارش معکوس",
        )
        Exam.objects.create(
            title="آزمون رسمی منقضی",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.PUBLISHED,
            counts_for_league=True,
            starts_at=now - timedelta(days=2),
            ends_at=now - timedelta(days=1),
        )
        Exam.objects.create(
            title="آزمون تمرینی آینده",
            kind=Exam.Kind.DAILY,
            status=Exam.Status.PUBLISHED,
            counts_for_league=False,
            starts_at=now + timedelta(hours=1),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(countdown.pk, [item["id"] for item in response.data])

    def test_countdown_slide_respects_its_own_active_window(self):
        now = timezone.now()
        hidden = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.EXAM_COUNTDOWN,
            title="شمارش خارج از بازه",
            starts_at=now + timedelta(hours=1),
        )
        visible = ShowcaseSlide.objects.create(
            kind=ShowcaseSlide.Kind.EXAM_COUNTDOWN,
            title="شمارش فعال",
            sort_order=1,
        )
        exam = Exam.objects.create(
            title="آزمون رسمی",
            kind=Exam.Kind.MOCK,
            status=Exam.Status.PUBLISHED,
            counts_for_league=True,
            starts_at=now + timedelta(hours=4),
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data], [visible.pk])
        self.assertEqual(response.data[0]["exam_title"], exam.title)
        self.assertNotIn(hidden.pk, [item["id"] for item in response.data])

    def test_uploaded_showcase_image_returns_root_absolute_media_url(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.client.force_authenticate(user=self.user)
                slide = ShowcaseSlide.objects.create(
                    kind=ShowcaseSlide.Kind.ADVERTISEMENT,
                    title="تصویر آزمایشی",
                    image=SimpleUploadedFile(
                        "banner.jpg", b"test-image-content", content_type="image/jpeg"
                    ),
                )

                response = self.client.get(self.url)

                self.assertEqual(response.status_code, 200)
                item = next(row for row in response.data if row["id"] == slide.pk)
                self.assertEqual(
                    item["image_url"],
                    "http://testserver/media/showcase/banner.jpg",
                )
