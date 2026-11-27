from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.exams.models import Exam, ExamAttempt
from apps.league.models import (
    LeagueSeason,
    LeagueScoreEntry,
    LeagueScoreAdjustment,
)
from apps.payments.models import PaymentOrder
from apps.subscriptions.models import SubscriptionPlan, UserSubscription


User = get_user_model()


class LeagueFeatureAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number="09120000001",
            display_name="کاربر اول",
            province="خوزستان",
            province_verified=True,
        )
        self.client.force_authenticate(self.user)

        now = timezone.now()
        self.season = LeagueSeason.objects.create(
            title="فصل آزمایشی",
            starts_at=now - timedelta(days=30),
            ends_at=now + timedelta(days=30),
            status=LeagueSeason.Status.ACTIVE,
        )

    def make_exam(
        self, title, ends_at=None, kind=Exam.Kind.NIGHT,
        status=Exam.Status.PUBLISHED,
    ):
        now = timezone.now()
        return Exam.objects.create(
            title=title,
            kind=kind,
            duration_minutes=30,
            max_attempts=5,
            starts_at=now - timedelta(days=2),
            ends_at=ends_at or now - timedelta(hours=1),
            status=status,
            counts_for_league=(kind == Exam.Kind.NIGHT),
            requires_purchase=False,
            price_irr=0,
        )

    def make_entry(self, exam, user, score, correct, wrong, elapsed):
        now = timezone.now()
        attempt = ExamAttempt.objects.create(
            exam=exam,
            user=user,
            status=ExamAttempt.Status.SUBMITTED,
            started_at=now - timedelta(minutes=30),
            deadline_at=now + timedelta(minutes=1),
            submitted_at=now,
            score=score,
            correct_count=correct,
            wrong_count=wrong,
            blank_count=0,
        )
        return LeagueScoreEntry.objects.create(
            season=self.season,
            attempt=attempt,
            user=user,
            score=score,
            correct_count=correct,
            wrong_count=wrong,
            elapsed_seconds=elapsed,
        )

    def activate_subscription(self):
        plan = SubscriptionPlan.objects.create(
            title="اشتراک آزمایشی",
            period=SubscriptionPlan.Period.MONTHLY,
            duration_days=30,
            price_irr=1990000,
            is_active=True,
        )
        order = PaymentOrder.objects.create(
            user=self.user,
            product_type=PaymentOrder.ProductType.SUBSCRIPTION,
            payment_provider=PaymentOrder.PaymentProvider.MANUAL,
            plan=plan,
            amount_irr=plan.price_irr,
            plan_duration_days_snapshot=plan.duration_days,
            status=PaymentOrder.Status.APPROVED,
        )
        now = timezone.now()
        return UserSubscription.objects.create(
            user=self.user,
            plan=plan,
            starts_at=now - timedelta(minutes=1),
            ends_at=now + timedelta(days=30),
            status=UserSubscription.Status.ACTIVE,
            source_order=order,
        )

    def test_latest_night_leaderboard_is_free_and_deduplicates_user(self):
        exam = self.make_exam("آزمون شبانه اخیر")
        self.make_entry(exam, self.user, 70, 7, 2, 600)
        best = self.make_entry(exam, self.user, 90, 9, 0, 500)

        response = self.client.get("/api/v1/league/latest-night-exam/")

        self.assertEqual(response.status_code, 200)
        rows = response.data["national_results"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["attempt_id"], str(best.attempt_id))
        self.assertEqual(rows[0]["total_score"], 90)

    def test_latest_exam_does_not_fallback_when_latest_has_no_entries(self):
        self.make_entry(
            self.make_exam("آزمون قدیمی"),
            self.user, 90, 9, 0, 500,
        )
        self.make_exam("آزمون جدید بدون شرکت‌کننده")

        response = self.client.get("/api/v1/league/latest-night-exam/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["national_results"], [])

    def test_appeal_adjustment_is_in_latest_leaderboard(self):
        exam = self.make_exam("آزمون با اصلاح امتیاز")
        entry = self.make_entry(exam, self.user, 70, 7, 2, 600)
        LeagueScoreAdjustment.objects.create(
            entry=entry,
            actor=self.user,
            score_delta=15,
            reason="اصلاح آزمایشی",
        )

        response = self.client.get("/api/v1/league/latest-night-exam/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["national_results"][0]["total_score"], 85)

    def test_provincial_results_only_include_verified_province(self):
        exam = self.make_exam("آزمون استانی")
        self.make_entry(exam, self.user, 80, 8, 1, 600)

        unverified = User.objects.create_user(
            phone_number="09120000002",
            display_name="استان تأییدنشده",
            province="خوزستان",
            province_verified=False,
        )
        self.make_entry(exam, unverified, 100, 10, 0, 400)

        response = self.client.get("/api/v1/league/latest-night-exam/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["provincial_results"]), 1)
        self.assertEqual(
            response.data["provincial_results"][0]["display_name"],
            self.user.display_name,
        )

    def test_top_five_is_free_and_contains_best_attempt_per_exam(self):
        exam1 = self.make_exam("آزمون اول")
        self.make_entry(exam1, self.user, 50, 5, 2, 600)
        best = self.make_entry(exam1, self.user, 80, 8, 1, 500)

        exam2 = self.make_exam("آزمون دوم")
        self.make_entry(exam2, self.user, 75, 7, 1, 550)

        response = self.client.get("/api/v1/league/me/top-records/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["attempt_id"], str(best.attempt_id))

    def test_top_records_exclude_draft_and_future_exams_but_include_archived(self):
        draft = self.make_exam(
            "آزمون پیش‌نویس",
            status=Exam.Status.DRAFT,
        )
        self.make_entry(draft, self.user, 100, 10, 0, 300)

        future = self.make_exam(
            "آزمون آینده",
            ends_at=timezone.now() + timedelta(days=1),
        )
        self.make_entry(future, self.user, 99, 10, 0, 310)

        archived = self.make_exam(
            "آزمون بایگانی‌شده",
            status=Exam.Status.ARCHIVED,
        )
        archived_entry = self.make_entry(
            archived, self.user, 80, 8, 1, 500
        )

        response = self.client.get("/api/v1/league/me/top-records/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["attempt_id"],
            str(archived_entry.attempt_id),
        )

    def test_analytics_requires_active_subscription(self):
        response = self.client.get("/api/v1/league/me/analytics/")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.data["subscription_required"])

    def test_analytics_is_available_with_active_subscription(self):
        self.activate_subscription()

        response = self.client.get("/api/v1/league/me/analytics/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["active"])
        self.assertIn("summary", response.data)

    def test_free_endpoints_require_authentication_but_not_subscription(self):
        self.client.force_authenticate(user=None)

        latest = self.client.get("/api/v1/league/latest-night-exam/")
        top = self.client.get("/api/v1/league/me/top-records/")

        self.assertEqual(latest.status_code, 401)
        self.assertEqual(top.status_code, 401)
