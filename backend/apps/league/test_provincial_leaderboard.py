from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.exams.models import Exam, ExamAttempt
from apps.league.models import LeagueSeason
from apps.league.services import record_attempt_score


class ProvincialLeaderboardTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.season = LeagueSeason.objects.create(
            title="فصل آزمایشی",
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=30),
            status=LeagueSeason.Status.ACTIVE,
        )
        self.exam = Exam.objects.create(
            title="آزمون آزمایشی",
            kind=Exam.Kind.NIGHT,
            status=Exam.Status.PUBLISHED,
            max_attempts=0,
            counts_for_league=True,
        )
        self.user = User.objects.create_user(
            "09120000011", province="تهران", province_verified=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _add_score(self, user, score):
        now = timezone.now()
        attempt = ExamAttempt.objects.create(
            exam=self.exam,
            user=user,
            status=ExamAttempt.Status.SUBMITTED,
            started_at=now - timedelta(minutes=5),
            deadline_at=now + timedelta(minutes=25),
            submitted_at=now,
            score=score,
            correct_count=score // 10,
            wrong_count=0,
            blank_count=0,
        )
        return record_attempt_score(attempt.pk)

    def test_provincial_board_includes_only_verified_users_in_same_province(self):
        same_province = User.objects.create_user(
            "09120000012", province="تهران", province_verified=True
        )
        unverified = User.objects.create_user(
            "09120000013", province="تهران", province_verified=False
        )
        other_province = User.objects.create_user(
            "09120000014", province="اصفهان", province_verified=True
        )
        self._add_score(self.user, 80)
        self._add_score(same_province, 90)
        self._add_score(unverified, 100)
        self._add_score(other_province, 110)

        response = self.client.get("/api/v1/league/provincial-leaderboard/?limit=20")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["verified"])
        self.assertEqual(response.data["province"], "تهران")
        self.assertEqual(
            [row["display_name"] for row in response.data["results"]],
            ["کاربر", "کاربر"],
        )
        self.assertEqual(
            [row["total_score"] for row in response.data["results"]],
            [90, 80],
        )

    def test_unverified_province_does_not_show_a_provincial_ranking(self):
        self.user.province_verified = False
        self.user.save(update_fields=["province_verified"])

        response = self.client.get("/api/v1/league/provincial-leaderboard/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["verified"])
        self.assertEqual(response.data["results"], [])

    def test_provincial_board_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/v1/league/provincial-leaderboard/")

        self.assertEqual(response.status_code, 401)
